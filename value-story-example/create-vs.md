# Create a Value Story

This document outlines the steps to create a new Value Story within the AVS framework.

## Step 1: Define the Goal

- **Objective:** Clearly define what you want to achieve with this Value Story.
- **Outcome:** Specify the desired output or result of executing the instructions.

## Step 2: Write Instructions

- **Logic:** Provide detailed, step-by-step instructions for achieving the goal. Ensure these are precise and unambiguous.
- **Algorithmically Legible:** The instructions should be understandable by both humans and AI agents.

## Step 3: Identify Context-Manifest

- **Data Sources:** List all external files, data sources, or APIs needed to execute the task.
- **Context-Rich:** Include any necessary context that will help prevent "context blindness."

## Step 4: Assemble the YAML Prompt

- **Automation Script:** Use `assemble_prompt.py` to combine the goal, instructions, and context-manifest into a single YAML file.
- **Execution:** Provide this YAML file as input to your AI agent.

# Example

### Goal
Create a markdown file for Gitbut to demon the thought process for creating a Value Story.

### Instructions
1. Draft goal (see above), instructions (here), and Context-Manfiest (below).
2. Create `assembly.py` python script to combine the goal, instructions and content identified in the Context-Manifest section into a YAML file (see `illustrative-example/assemble_prompt.py` for an example of the desire YAML structure.)
3. Run the newly created py script and save the output as create-vs.yaml
4. Read the new create-vs.yaml and treat is as if it were an input prompt.

