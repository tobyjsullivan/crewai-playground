import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from typing import List
from .tools.custom_tool import WeatherForcastTool

weather_forcast_tool = WeatherForcastTool()

user_preference = TextFileKnowledgeSource(
    file_paths=['user_preference.txt'],
    name='User Preference',
    description='User preference'
)

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
# @before_kickoff
# def before_kickoff():
#     # Create the output directory if it doesn't exist
#     os.makedirs('output', exist_ok=True)


@CrewBase
class WeatherChecker():
    """WeatherChecker crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def personal_assistant(self) -> Agent:
        return Agent(
            config=self.agents_config['personal_assistant'], # type: ignore[index]
            allow_delegation=True,
            verbose=True
        )

    @agent
    def weather_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['weather_reporter'], # type: ignore[index]
            verbose=True,
            tools=[weather_forcast_tool]
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def lookup_current_weather(self) -> Task:
        return Task(
            config=self.tasks_config['lookup_current_weather'], # type: ignore[index]
        )

    @task
    def write_morning_update(self) -> Task:
        return Task(
            config=self.tasks_config['write_morning_update'], # type: ignore[index]
        )


    @crew
    def crew(self) -> Crew:
        """Creates the WeatherChecker crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            # manager_agent=self.personal_assistant,
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
            # planning=True,
            knowledge_sources=[user_preference]
        )
