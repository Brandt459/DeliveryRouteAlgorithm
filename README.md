# Problem

For my Data Structures and Algorithms II class, I was tasked with developing a solution to optimize the delivery of 40 packages using three trucks with a limited capacity of 16 packages each. The delivery routes had to take into account the delivery deadlines and locations of each package and the total combined mileage could not exceed 140 miles.
# Solution

To tackle this issue, I employed the use of a greedy algorithm to determine an efficient delivery route for the packages. The algorithm was designed to prioritize packages with the closest delivery deadline, but also considered the proximity of the next location to minimize the total combined mileage. The solution was implemented using Python and leveraged the chaining hash table data structure to effectively store and retrieve relevant data.
# Challenges and Lessons Learned

The development of this solution was not without its challenges, as my initial solution resulted in a total combined mileage exceeding the 140-mile limit. However, through diligent analysis and iteration, I identified that the algorithm was not properly considering the delivery of multiple packages to the same location. I made the necessary modifications to address this issue, and as a result, the total combined mileage was reduced from 165 miles to 127 miles.

This project provided valuable learning experiences in terms of problem-solving and perseverance. I honed my attention to detail as I had to constantly evaluate and adjust the algorithm to meet the requirements. Additionally, I gained experience working with Python and strengthened my understanding of the use of chaining hash tables. 
