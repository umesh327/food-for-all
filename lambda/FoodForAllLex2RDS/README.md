# Food for All 

## Introduction

According to a report by [The Atlantic](https://www.theatlantic.com/business/archive/2016/07/american-food-waste/491513/), each year in USA alone roughly 50% of all produce is thrown away. This amounts to about 60 million tons of food costing around $160 billion.  Sadly, about [49 million americans](https://www.dosomething.org/facts/11-facts-about-hunger-us) struggle to put food on the table. 

## Problem

After speaking to several food pantries and interviewing several grocery stores, the problem is finding and matching the food producers with the family that are going hungry. There are several mobile apps that tried to solve this problem. But most (if not all) of these applications cater to local markets. There are no apps currently that any local patron or donor could use to exchange food. 

## Solution 

Food for All serverless application works as follows:
1. Any user would like to either donate, receive food would register with the service by sending a text message "Register" to (551) 231 7912. After that the application will ask a series of questions to collect data from the user. 
2. Once a user is registered, they can check their registration status by sending a text "find me" to above number.  If they were already registered, they will receive a text message confirming their status.
3. When a user is ready to donate food, they would send a text "donate" to above number and a couple of questions would be asked to identify the type of food and expiry. After this, the application will try to find any patrons available within 5 miles of donor's address. If any found, the application will send details of donor to patron and vice versa.
4. 
