import random

VERBOSE = True

# Global goals with initial values
goals = {
    'Eat': 8,  # Changing value to demonstrate SGI
    'Sleep': 4,  # Changing value to demonstrate SGI
}

# Global (read-only) actions and effects
actions = {
    'get raw food': {'Eat': -3},
    'get snack': {'Eat': -2},
    'sleep in bed': {'Sleep': -4},
    'sleep on sofa': {'Sleep': -2},
}


def apply_action(action):
    '''Change all goal values using this action. An action can change multiple
    goals (positive and negative side effects).
    Negative changes are limited to a minimum goal value of 0.
    '''
    for goal, change in actions[action].items():
        goals[goal] = max(goals[goal] + change, 0)


def action_utility(action, goal):
    '''Return the 'value' of using "action" to achieve "goal".

    For example::
        action_utility('get raw food', 'Eat')

    returns a number representing the effect that getting raw food has on our
    'Eat' goal. Larger (more positive) numbers mean the action is more
    beneficial.
    '''
    if goal in actions[action]:
        # Is the goal affected by the specified action?
        return -actions[action][goal]
    else:
        # It isn't, so utility is zero.
        return 0


def choose_action():
    assert len(goals) > 0, 'Need at least one goal'
    assert len(actions) > 0, 'Need at least one action'

    # Find the most insistent goal
    best_goal, _ = max(goals.items(), key=lambda item: item[1])

    # Get all actions that affect the most insistent goal
    possible_actions = [key for key, value in actions.items() if best_goal in value]

    # Randomly shuffle the actions to avoid repeating the same action consecutively
    random.shuffle(possible_actions)

    # Select the first action from the shuffled list
    return possible_actions[0]


#==============================================================================

def print_actions():
    print('ACTIONS:')
    for name, effects in actions.items():
        print(" * [%s]: %s" % (name, str(effects)))


def run_until_all_goals_zero():
    HR = '-' * 40
    print_actions()
    print('>> Start <<')
    print(HR)
    running = True
    while running:
        print('GOALS:', goals)
        # What is the best action
        action = choose_action()
        print('BEST ACTION:', action)
        # Apply the best action
        apply_action(action)
        print('NEW GOALS:', goals)
        # Stop?
        if all(value == 0 for goal, value in goals.items()):
            running = False
        print(HR)
    # finished
    print('>> Done! <<')


if __name__ == '__main__':
    run_until_all_goals_zero()
