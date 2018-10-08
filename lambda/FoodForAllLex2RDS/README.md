# Food for All 

## Introduction

According to a report by [The Atlantic](https://www.theatlantic.com/business/archive/2016/07/american-food-waste/491513/), each year in USA alone roughly 50% of all produce is thrown away. This amounts to about 60 million tons of food costing around $160 billion.  Sadly, about [49 million americans](https://www.dosomething.org/facts/11-facts-about-hunger-us) struggle to put food on the table. 

## Problem

After speaking to several food pantries and interviewing several grocery stores, the problem is finding and matching the food producers with the family that are going hungry. There are several mobile apps that tried to solve this problem. But most (if not all) of these applications cater to local markets. There are no apps currently that any local patron or donor could use to exchange food. 

## Solution 

Food for All serverless application works as follows:
1. Users register for the first time using a SMS Chatbot.
2. After initial registration, a donor can submit a donation anytime by simply sending a text message.
3. Every time a new donation is made, app backend will use a geo spatial query to find nearest patrons within 5 miles from the donor, sends them a text message if they want to accept the food donation.
