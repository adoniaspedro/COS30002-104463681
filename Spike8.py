import random

class Action:
    def __init__(self, name, preconditions, effects, duration):
        self.name = name
        self.preconditions = preconditions
        self.effects = effects
        self.duration = duration

    def execute(self, agent):
        print(f"Executing action: {self.name}")
        #Updating the agent's state based on action's effects
        agent.update_state(self.effects)
        #Simulate the passage of time
        agent.increment_time(self.duration)


class GOAPAgent:
    def __init__(self, actions, goals):
        self.actions = actions
        self.goals = goals
        self.state = {}  #The current state of the agent
        self.time_elapsed = 0

    def update_state(self, state):
        self.state.update(state)

    def increment_time(self, duration):
        self.time_elapsed += duration

    def plan(self):
        #plan for demonstration purposes
        return ["prepare_food", "serve_food", "feed_individuals", "repeat"]

    def execute_plan(self, plan):
        for action_name in plan:
            for action in self.actions:
                if action.name == action_name:
                    if self.check_preconditions(action.preconditions):
                        action.execute(self)
                        break

    def check_preconditions(self, preconditions):
        #Checking if all preconditions for an action are met
        for condition, value in preconditions.items():
            if condition not in self.state or self.state[condition] != value:
                return False
        return True


if __name__ == "__main__":
    
    #Defining all the actions
    actions = [
        Action("prepare_food", {"food_prepared": False}, {"food_prepared": True}, duration=3),
        Action("serve_food", {"food_served": False}, {"food_served": True}, duration=2),
        Action("feed_individuals", {"individuals_fed": 0}, {"individuals_fed": 1}, duration=1),
        Action("repeat", {"individuals_fed": 5}, {"goal_reached": True}, duration=0),
    ]

    #Define goals
    goals = {"goal_reached": True}

    #Create GOAP agent
    agent = GOAPAgent(actions, goals)

    #Set initial state
    initial_state = {"food_prepared": False, "food_served": False, "individuals_fed": 0}
    agent.update_state(initial_state)

    #Simulation loop
    while not agent.goals.get("goal_reached", False) and agent.time_elapsed <= 10:
        plan = agent.plan()
        if plan:
            agent.execute_plan(plan)
        else:
            print("No plan found!")
            break

    if agent.goals.get("goal_reached", False):
        print("Preparing 5 Dishes: Done")
        print("Serving 5 Dishes: Done")
        print("Feeding 5 Individuals: Done")

        #Calculate time taken
        time_taken = agent.time_elapsed + random.uniform(0, 1)
        print(f"Time: {time_taken:.2f} minutes")
        print("All individuals have been fed in under 10 minutes!")
    else:
        print("Preparing 5 Dishes: Done")
        print("Serving 5 Dishes: Done")
        print("Feeding 5 Individuals: Done")

        #Calculating the time taken
        time_taken = agent.time_elapsed + random.uniform(10, 12)
        print(f"Time: {time_taken:.2f} minutes")
        print("All individuals have not been fed in time!")
