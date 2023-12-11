# Automated Experiment Design Domain

## Context

The 'Automated Experiment Design Domain TSB' aims at improving efficiency and flexibility of an industrial scenario at Procter&Gamble, where robots are employed to support people in the development of automated quality tests, considering in particular testing laundry detergent soluble pouches. 

Quality tests consist in measuring certain pouch features, such as weight, dimensions, film elasticity, tightness, strength (resistance to compression), and are typically carried out by a human operator cooperating with a robotic arm, using different measure instruments. Since instruments can operate with several settings (e.g., strength can be tested by applying constant compression force, constant compression rate, a mix of the two, etc.) and tests may need different settings, the overall procedure varies in each testing session.

Typical operations include:
- Picking up individual pouches from product containers
- Identifying pouches (production codes, production line, etc.) and labeling in the data system
- Deciding the sequence of tests to carry out, based on pouch type and project
- Placing each pouch in the specific instrument
- Setting up and operating the instruments
- Recording results
- Recording visual observations, such as possible breakage area or type of failure
- Disposing the pouch

<img src='img/automated-experiments.png' width='350'>
<!--![Automated Experiments](img/automated-experiments.png | width="100")-->

Manually handling the overall procedure is a very intensive task, which may employ many people for entire days. Moreover, the robotic arm requires being re-programmed every time a change in the procedure is to be applied. 

The main goal of the 'Automated Experiment Design Domain' TSB is to demonstrate the effectiveness of AI planning technology integrated with robotics solutions in delivering a high number of robotics procedures for the various use-cases, while reducing manual operations and planning that currently limit flexibility and efficiency of the system. Moreover, the TSB aims at empowering non-robotics-experts to be able to customise, adapt, and change the course of the robotics procedures, using natural interfaces.

## Planning Problem Description

The planning problem in question revolves around a rover designed for Mars exploration, serving as the central agent. This Mars rover exhibits a versatile range of capabilities, enabling it to engage in various activities and tasks essential for scientific research and exploration on the Martian surface. The primary objective is to construct a sequential plan that outlines a series of actions the rover must undertake to achieve a specific mission goal. The complexity of this planning task is compounded by the presence of mission timelines and deadlines, closely tied to specific communication windows with Earth, where the rover must transmit data and receive instructions. Furthermore, the rover must manage its limited resources, such as battery power and available data storage, adding an additional layer of complexity. The mission's overarching goal is framed as a partial plan, necessitating planning to transform it into a fully executable and successful mission on Mars.

## Modeling in UP

The problem is modelled using the Unified Planning (UP) framework through the specification of predicates and actions needed to describe the application domain. The level of abstraction of predicates and actions has been tuned with a bottom-up approach, where procedures implementing predicate and action functionalities have been first developed and tested on the real scenario and in the simulator to guarantee applicability and then they have been described as domain and problem specifications using the UP framework. We defined different domains and problems to show the flexibility of the solution and we used both single-agent and multi-agent formalizations in order to improve the effectiveness of the solution.

Two modeling approaches where considered. One uses Multi-Agent Planning which, by modeling the various measure instruments as distinct agents, 
naturally enables parallel and independent execution of the measure instruments, which in turn leads to significant saving in execution time, wrt sequential solutions, where instruments run sequentially.  As to the second, called 'post-parallelization' approach, in order to further increase the saving in execution time, instead of solving the original problem instance, a simplified version on a smaller number of pouches was solved, and several replicas of the resulting plan were then combined in parallel, so as to deal with the original number of pouches. This latter approach resulted the most effective.

## Operation Modes and Integration Aspects

The `OneShotPlanner` mode was used to produce the solution plan. This is the simpolest way to obtain a plan for an input problem instance. 
The `Sequential Simulator` mode was used for combining and parallelizing the plans that solve the easier problem, in the post-parallelization approach. The `Compiler` mode was used to switch from a multi-agent to a sequential representation of the problem in the post-parallelization approach.



## Lessons Learned


## Resources

- [Planning for Space page](https://www.ai4europe.eu/business-and-industry/case-studies/planning-space)
- TSB for the Space Use Case. [Github](https://github.com/aiplan4eu/tsb-space)
