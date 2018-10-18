# FIT2107 - Assignment 3 - Test Strategy


**Statement Coverage**

For all test cases, the primary techniques utilised were white box techniques. Statement coverage using `coverage` was
considered, especially for runnning assertion test cases where the aim is to trigger every pre-condition check and
assert that an exception (`IllegalArgumentException`) is raised. As this program was coded with some adherence to 
design-by-contract, assertion checks make up a large proportion of our program and test cases. The aim is to maintain
a high coverage percentage, but not 100% as it is infeasible (and sometimes impossible) to cover every possible line.

**Branch Coverage**

Branch coverage is then also considered, primarily for `if` and `for` statements. For any `if` statements, the goal
is to trigger both conditions of the statement (assuming simple logical comparison), and for `for` statements, the
goal is to consider three situations: where the loop is never entered, where the loop runs once, and where the loop
runs multiple times. 

**Correctness & Mocking**

Functional correctness is tested across the system and at a single functional level. Mocking is used to simulate 
satellite data to remove the need for some calls to the _Skyfield_ library and also to the satellite data source 
(_Celestrak NORAD_ in this case). However the _Skyfield_ library is to be called at least once while testing the
system overall (i.e. running `find_time()`). 

