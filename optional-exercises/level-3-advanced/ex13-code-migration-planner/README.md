# Exercise 13: Code Migration Planner

## Description
Intelligent system to plan and execute code migrations between frameworks/languages.

## Objectives
- Analyze complete codebase
- Generate detailed migration plan
- Identify dependencies and blockers
- Estimate effort and risks
- Generate migrated code progressively

## Use Cases

- JavaScript → TypeScript
- React Class Components → Hooks
- Django → FastAPI
- REST → GraphQL
- SQL → NoSQL
- Python 2 → Python 3

## Architecture

```
Analyze Codebase → Dependency Graph → Migration Plan → Execute → Validate
```

## Core Implementation

```python
from dataclasses import dataclass
from typing import List, Dict
import networkx as nx

@dataclass
class MigrationTask:
    id: str
    description: str
    file: str
    dependencies: List[str]
    estimated_effort: str  # "small", "medium", "large"
    risk_level: str  # "low", "medium", "high"
    code_before: str
    code_after: str | None = None

class MigrationPlanner:
    def __init__(self, source_framework: str, target_framework: str):
        self.source = source_framework
        self.target = target_framework
        self.llm = ChatAnthropic(model="claude-sonnet-4")

    async def analyze_codebase(self, directory: str) -> Dict:
        """Analyze entire codebase to understand structure"""
        print(f"📊 Analyzing codebase in {directory}...")

        # 1. Find all relevant files
        files = self._find_files(directory)

        # 2. Analyze each file
        analyses = []
        for file in files:
            analysis = await self._analyze_file(file)
            analyses.append(analysis)

        # 3. Build dependency graph
        dep_graph = self._build_dependency_graph(analyses)

        return {
            "files": files,
            "analyses": analyses,
            "dependencies": dep_graph,
            "stats": self._calculate_stats(analyses)
        }

    async def _analyze_file(self, file_path: str) -> Dict:
        """Analyze single file for migration requirements"""
        with open(file_path, 'r') as f:
            code = f.read()

        prompt = f"""
Analyze this {self.source} code for migration to {self.target}:

{code}

Identify:
1. Key constructs that need migration
2. Dependencies on other modules
3. Potential challenges
4. Migration priority (1-5)

Respond in JSON format.
"""

        response = await self.llm.ainvoke(prompt)
        return json.loads(response.content)

    async def create_migration_plan(self, analysis: Dict) -> List[MigrationTask]:
        """Generate ordered migration plan"""
        print("📝 Creating migration plan...")

        tasks = []
        dep_graph = analysis['dependencies']

        # Topological sort for proper ordering
        ordered_files = list(nx.topological_sort(dep_graph))

        for file in ordered_files:
            file_analysis = analysis['analyses'][file]

            # Generate migration tasks for this file
            file_tasks = await self._generate_file_tasks(
                file,
                file_analysis
            )

            tasks.extend(file_tasks)

        return self._optimize_plan(tasks)

    async def _generate_file_tasks(
        self,
        file: str,
        analysis: Dict
    ) -> List[MigrationTask]:
        """Generate migration tasks for a single file"""

        prompt = f"""
Create detailed migration tasks for this file:

File: {file}
Analysis: {json.dumps(analysis, indent=2)}

Source: {self.source}
Target: {self.target}

For each construct that needs migration, create a task with:
- Description
- Dependencies (other tasks that must complete first)
- Estimated effort
- Risk level
- Code transformation

Output as JSON array of tasks.
"""

        response = await self.llm.ainvoke(prompt)
        tasks_data = json.loads(response.content)

        return [
            MigrationTask(
                id=f"{file}_{i}",
                file=file,
                **task_data
            )
            for i, task_data in enumerate(tasks_data)
        ]

    async def execute_task(self, task: MigrationTask) -> bool:
        """Execute a single migration task"""
        print(f"⚙️  Executing: {task.description}")

        # Generate migrated code
        migrated_code = await self._migrate_code(task)

        # Validate migrated code
        is_valid = await self._validate_code(migrated_code, task.file)

        if is_valid:
            # Apply migration
            self._apply_migration(task.file, task.code_before, migrated_code)
            task.code_after = migrated_code
            return True
        else:
            print(f"❌ Validation failed for {task.description}")
            return False

    async def _migrate_code(self, task: MigrationTask) -> str:
        """Generate migrated code"""
        prompt = f"""
Migrate this {self.source} code to {self.target}:

{task.code_before}

Requirements:
- {task.description}

Provide only the migrated code, no explanation.
"""

        response = await self.llm.ainvoke(prompt)
        return response.content

    async def _validate_code(self, code: str, file: str) -> bool:
        """Validate migrated code"""
        # 1. Syntax check
        try:
            compile(code, file, 'exec')
        except SyntaxError:
            return False

        # 2. Run tests (if available)
        test_result = subprocess.run(
            ['pytest', f'tests/{file}', '-v'],
            capture_output=True
        )

        return test_result.returncode == 0
```

## Example Usage

```python
# Migrate React Class → Hooks
planner = MigrationPlanner(
    source_framework="react-class",
    target_framework="react-hooks"
)

# Analyze codebase
analysis = await planner.analyze_codebase('./src')

# Create migration plan
plan = await planner.create_migration_plan(analysis)

print(f"\n📋 Migration Plan ({len(plan)} tasks)")
print("=" * 60)

for task in plan:
    print(f"\n{task.id}: {task.description}")
    print(f"  File: {task.file}")
    print(f"  Effort: {task.estimated_effort}")
    print(f"  Risk: {task.risk_level}")
    print(f"  Dependencies: {task.dependencies}")

# Execute plan
print("\n🚀 Starting migration...")
for task in plan:
    success = await planner.execute_task(task)
    if not success:
        print(f"⚠️  Stopping due to failure in {task.id}")
        break

print("\n✅ Migration complete!")
```

## Advanced Features

### 1. Risk Analysis

```python
class RiskAnalyzer:
    def analyze_risks(self, plan: List[MigrationTask]) -> Dict:
        risks = {
            "high_risk_tasks": [],
            "breaking_changes": [],
            "effort_estimate": 0
        }

        for task in plan:
            if task.risk_level == "high":
                risks["high_risk_tasks"].append(task)

            if "breaking" in task.description.lower():
                risks["breaking_changes"].append(task)

            # Estimate hours
            effort_map = {"small": 2, "medium": 8, "large": 16}
            risks["effort_estimate"] += effort_map[task.estimated_effort]

        return risks
```

### 2. Progressive Migration

```python
class ProgressiveMigrator:
    """Migrate incrementally, keeping old code working"""

    async def migrate_with_fallback(self, task: MigrationTask):
        # Create new version alongside old
        new_file = task.file.replace('.js', '.new.js')

        with open(new_file, 'w') as f:
            f.write(task.code_after)

        # Add feature flag
        add_feature_flag(task.file, new_file)

        # Validate new version
        if await self.validate_with_tests():
            # Gradually switch traffic
            await self.gradual_rollout(task.file, new_file)
        else:
            print("Keeping old version due to test failures")
```

### 3. Report Generation

```python
def generate_migration_report(
    plan: List[MigrationTask],
    completed: List[MigrationTask]
) -> str:
    """Generate detailed migration report"""

    report = f"""
# Migration Report: {source} → {target}

## Summary
- Total Tasks: {len(plan)}
- Completed: {len(completed)}
- Remaining: {len(plan) - len(completed)}
- Estimated Effort: {calculate_effort(plan)} hours

## Completed Tasks
{format_tasks(completed)}

## Remaining Tasks
{format_tasks([t for t in plan if t not in completed])}

## Risks Identified
{list_risks(plan)}

## Recommendations
{generate_recommendations(plan, completed)}
"""

    return report
```

## Testing

```python
def test_dependency_ordering():
    """Ensure tasks are ordered by dependencies"""
    planner = MigrationPlanner("js", "ts")

    tasks = [
        MigrationTask("1", "Migrate utils", "utils.js", []),
        MigrationTask("2", "Migrate app", "app.js", ["1"]),
    ]

    ordered = planner._optimize_plan(tasks)

    assert ordered[0].id == "1"
    assert ordered[1].id == "2"

def test_validation():
    """Test code validation"""
    planner = MigrationPlanner("python2", "python3")

    # Valid Python 3 code
    valid = await planner._validate_code("print('hello')", "test.py")
    assert valid

    # Invalid syntax
    invalid = await planner._validate_code("print 'hello'", "test.py")
    assert not invalid
```

## Challenges Extra

1. **AI-Assisted Review**: LLM reviews migrations before applying
2. **Rollback Mechanism**: Automatic rollback on failures
3. **Performance Benchmarking**: Compare old vs new performance
4. **Documentation Migration**: Update docs alongside code

## Resources
- [AST (Abstract Syntax Tree)](https://docs.python.org/3/library/ast.html)
- [NetworkX for Graphs](https://networkx.org/)
- [Codemod Tools](https://github.com/facebook/codemod)

**Time**: 7-9h
