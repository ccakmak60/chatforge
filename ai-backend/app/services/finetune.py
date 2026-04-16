import asyncio
import os

import mlflow
import wandb
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset

from app.config import settings
from app.schemas import FinetuneResponse


async def run_lora_finetune(
    base_model: str,
    dataset_path: str,
    output_dir: str,
    num_epochs: int,
    learning_rate: float,
    lora_r: int,
    lora_alpha: int,
) -> str:
    def _train():
        tokenizer = AutoTokenizer.from_pretrained(base_model)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            base_model, device_map="auto", torch_dtype="auto"
        )

        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=lora_r,
            lora_alpha=lora_alpha,
            lora_dropout=0.05,
            target_modules=["q_proj", "v_proj"],
        )
        model = get_peft_model(model, lora_config)

        dataset = load_dataset("json", data_files=dataset_path, split="train")

        def tokenize(example):
            return tokenizer(
                example["text"], truncation=True, padding="max_length", max_length=512
            )

        dataset = dataset.map(tokenize, batched=True, remove_columns=dataset.column_names)
        dataset = dataset.add_column("labels", dataset["input_ids"])

        from transformers import Trainer

        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            learning_rate=learning_rate,
            per_device_train_batch_size=4,
            save_strategy="epoch",
            logging_steps=10,
            report_to=["wandb"],
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=dataset,
            tokenizer=tokenizer,
        )
        trainer.train()
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        return output_dir

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _train)


class FinetuneService:
    async def launch(
        self,
        base_model: str,
        dataset_path: str,
        bot_id: str,
        num_epochs: int = 3,
        learning_rate: float = 2e-4,
        lora_r: int = 8,
        lora_alpha: int = 16,
    ) -> FinetuneResponse:
        model_name = f"{bot_id}-ft"
        output_dir = f"/tmp/chatforge_finetune/{model_name}"
        os.makedirs(output_dir, exist_ok=True)

        wandb.init(
            project=settings.wandb_project,
            name=f"finetune-{model_name}",
            config={
                "base_model": base_model,
                "num_epochs": num_epochs,
                "learning_rate": learning_rate,
                "lora_r": lora_r,
                "lora_alpha": lora_alpha,
            },
        )

        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        with mlflow.start_run(run_name=f"finetune-{model_name}") as run:
            mlflow.log_params({
                "base_model": base_model,
                "num_epochs": num_epochs,
                "learning_rate": learning_rate,
                "lora_r": lora_r,
                "lora_alpha": lora_alpha,
                "bot_id": bot_id,
            })

            output_path = await run_lora_finetune(
                base_model=base_model,
                dataset_path=dataset_path,
                output_dir=output_dir,
                num_epochs=num_epochs,
                learning_rate=learning_rate,
                lora_r=lora_r,
                lora_alpha=lora_alpha,
            )

            mlflow.log_artifacts(output_path, artifact_path="model")
            mlflow.log_param("output_dir", output_path)

            run_id = run.info.run_id

        wandb.finish()

        return FinetuneResponse(
            status="complete",
            run_id=run_id,
            model_name=model_name,
        )
