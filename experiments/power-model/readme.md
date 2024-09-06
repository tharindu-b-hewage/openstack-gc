## Power Modelling for Packing VMs on Green Cores

For the Green Cores VM packing algorithm, we use a core count based server power model.

$$
P_{S}(t) \simeq f(m(t) \times P_{PINNED} + l(t) \times P_{SLEEP} + (N - m(t) - l(t)) \times P_{ACTIVE})
$$

There are three states for a core.

- Pinned
- Active (= idle)
- Asleep

We model each state has a static power consumption.

The goal of this experiment is to show that this model is reasonable for an RT server, and power variations with 
core sleeping is significant in renewable harvesting.

### Part 01

1. Put all cores awake. Measure power.
2. Put core-by-core into the asleep state. Measure power.
3. Plot the power consumption.

This should provide demonstration of Active and Asleep power consumption.

### Part 02

Then, put all cores awake.

1. Keep packing 6 VMs with 2 vcpus each, one by one and measure power. Make sure that the VM runs RTEval and its utilization
reaches 100% before power measurement.
2. Plot the power consumption.

This should provide demonstration of Pinned power consumption.

Then, change renewables to zero. and plot the power drop. That should demonstrate the opportunity to harness power.

### Conclusion

In the end, this power model motivates the designed VM packing algorithm for Green Cores.