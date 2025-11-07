import os
import re

models_dir = "app/models"
models = {}

for filename in os.listdir(models_dir):
    if filename.endswith(".py") and filename not in ["__init__.py", "__pycache__"]:
        filepath = os.path.join(models_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()
            # Encontrar todas as classes que herdam de Base
            classes = re.findall(r'^class (\w+)\(Base\):', content, re.MULTILINE)
            if classes:
                module_name = filename[:-3]  # Remove .py
                models[module_name] = classes

print("=== MODELOS ENCONTRADOS ===")
for module, classes in sorted(models.items()):
    print(f"\n{module}.py:")
    for cls in classes:
        print(f"  - {cls}")
