#!/bin/bash
#SBATCH --job-name=run_experiment
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#SBATCH --partition=gpu-single
#SBATCH --gres=gpu:1
#SBATCH --time=24:00:00
#SBATCH --mem=70G

echo "Starting Ollama: $(date)"
ollama serve > logs/ollama_server.log 2>&1 &
sleep 10

echo "Checking Ollama connection"
curl http://127.0.0.1:11434/api/tags

echo "Pulling model"
ollama pull gpt-oss:20b

echo "Pipeline started: $(date)"


mkdir -p logs
mkdir -p outputs/characters
mkdir -p outputs/persona_prompts
mkdir -p outputs/attack_prompts
mkdir -p outputs/transcripts
mkdir -p outputs/results

echo "Pipeline started: $(date)"

python /gpfs/bwfor/home/ma/ma_ma/ma_ebasha/team-project-robustness1/pipeline/pull_ollama_models.py
echo "Pull Ollama models run successfully "
python /gpfs/bwfor/home/ma/ma_ma/ma_ebasha/team-project-robustness1/pipeline/start_pipeline_afresh.py
echo "Start pipeline afresh run successfully"
python /gpfs/bwfor/home/ma/ma_ma/ma_ebasha/team-project-robustness1/code/character_generation.py 
echo "character_generation successful"
python /gpfs/bwfor/home/ma/ma_ma/ma_ebasha/team-project-robustness1/code/persona_prompt_bundle_generation.py 
echo "persona_prompt_bundle_generation successful"
python /gpfs/bwfor/home/ma/ma_ma/ma_ebasha/team-project-robustness1/code/attack_prompt_bundle_generation.py 
echo "attack_prompt_bundle_generation successful"
python /gpfs/bwfor/home/ma/ma_ma/ma_ebasha/team-project-robustness1/code/transcript_generation.py 
echo "transcript_generation successful"
python /gpfs/bwfor/home/ma/ma_ma/ma_ebasha/team-project-robustness1/code/backup_transcript_generation.py
echo "backup transcript generation successful"

echo "Starting evaluation rounds: $(date)"
for round in $(seq 1 5); do
  echo "=== Evaluation round ${round} start: $(date) ==="

  while true; do
    python code/evaluation.py 2>&1 | tee -a logs/eval_round_${round}.log | grep -q "Evaluation is complete" && break
    echo "Round ${round} partial batch done; continuing..."
    sleep 5
  done

  python code/evaluation.py 2>&1 | tee -a logs/eval_round_${round}.log
  echo "Round ${round} merged partial results."
  echo "=== Evaluation round ${round} finished: $(date) ==="
done

echo "Evaluation rounds complete: $(date)"

python /gpfs/bwfor/home/ma/ma_ma/ma_ebasha/team-project-robustness1/code/combine_results.py 
echo "combine_results successful"
python /gpfs/bwfor/home/ma/ma_ma/ma_ebasha/team-project-robustness1/code/build_dashboard.py
echo "build_dashboard successful"

echo "Pipeline finished: $(date)"

