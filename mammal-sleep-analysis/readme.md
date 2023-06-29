# mammal-sleep-analysis
this was a quick sleep analysis inspired by "Why We Sleep: Unlocking the Power of Sleep and Dreams". 
I used the pantheria and mammal sleep datasets. 
My goal was to see the relationship between certain characteristics like brain/body size, metabolic factors, predation risk factors and social complexity affect sleep duration and architecture. I was able to reproduce and visualize known relationships. 
I attempted to use XGBoost, but I ran into issues overfitting. With 40 examples and lots of NaNs, it was difficult to model this. If I come back to this, I will try other methods like support vector machines, random forest or linear regreession. Next time, I'll try to find more data as well.
