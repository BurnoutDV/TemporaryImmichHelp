# Temporary Immich Help

With every day Immich gets more powerful and gains new utility, for now not everything is easily possible with the supplied tools. At one point my work here might be pointless, but for now this repository contains some quick scripts that help me facilitate more complex functions at the drop of a hat

## Features

### Deleting tags by Regex

_Background_ I use some ancient, cobbled together python gui to assign gps coordinates to camera pictures using an gpx file. This works fine, I played a bit with the settings during a period and one of those settings adds tags for the position, those are mighty useless, eg. _0.01 km north of Berlin_ and clutter the interface. I wanted them gone.

---
## Not yet implemented

### ReDate Whatsapp Images 

For reasons only known to past me I transport my whole WhatsApp Picture folder and everything from one Smartphone to another. At some point, in my case, April 2022 all pictures from before that lost their file date and now the files are cluttered and one specific day. This is annoying. The good news is, the files itself got the correct date in their name so its a solveable problem and I can enrich them with meta data.

### Rolling Back the deleted tags by the Regex Tag Deleter

Turns out, when deleting something, its actually quite easy to save that state and build an utility to roll all those changes back.

## Coding

I was really considering to build this as an Textual Interface but I am short in time and I just need the utility, no fancy. I firmly believe in Open Source so at least some attempt for resuability is made, but that's about it. We all will get eaten by vulture capitalists anyway.

if for some reasons I find time or just the feeling of creating something from the cold Abyss, I might reevaluate. Or if I find more niché functions that needs to be implemented.

All this really does is doing API calls anyway. So expect no wonders.