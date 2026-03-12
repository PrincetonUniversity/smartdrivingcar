---
layout: newsletter
title: "Wednesday, Feb. 9, 2022"
date: 2022-02-09
permalink: /10.24-Crashes-070922/
display_name: "10.24 - Crashes 070922"
---
July 9, 2022

24th edition of the 10th year of SmartDrivingCars eLetter

### [U.S. agency probing self-driving Cruise car crash in California](https://www.reuters.com/business/autos-transportation/us-agency-probing-cruise-crash-california-2022-07-07/)

D. Shepardson, July 7, "The National Highway Traffic Safety Administration has opened a special investigation into a recent crash of a Cruise self-driving vehicle in California that resulted in minor injuries, the agency said on Thursday.

The auto safety agency did not identify the specific crash, but a Cruise vehicle operating in driverless autonomous mode was involved in a crash involving minor injuries on June 3 in San Francisco, according to a [report filed](https://www.dmv.ca.gov/portal/file/cruise_060322-pdf) with the California Department of Motor Vehicles. ...

" [Read more](http://www.michaellsena.com/wp-content/uploads/2022/06/The-Dispatcher_July_2022.pdf) Hmmmm... The police report indicates that the Cruise vehicle stopped while making a protected left turn, yielding to avoid being T-boned by a speeding Prius that might run its red. Instead the Prius changed to its left turn lane and broadsided the Cruise vehicle. I can't wait to see the Cruise 360 video of that crash. Hopefully the Prius' insurance company will reimburse the Federal Government for its expenses incurred in its special investigation of the crash that it caused. Alain

### SmartDrivingCars [ZoomCast Episode 274](https://youtu.be/fHnC6pDlimI)/ [PodCast 2](https://anchor.fm/smartdrivingcars/episodes/Smart-Driving-Cars-Episode-268-Why-wireless-EV-charging-is-key-to-autonomous-mobility-e1iimbi) w/ [Anil Lewis](https://nfb.org/about-us/national-headquarters/executive-directors/anil-lewis) of the [National Federation of the Blind](https://nfb.org/) & [Katherine Freund](https://www.linkedin.com/in/katherinefreund), founder [ITN America](https://www.itnamerica.org/)

F. Fishkin, July 9, "More MOVES progress in NJ, NHTSA investigates a Cruise crash, and two fatal Tesla crashes, Musk makes more headlines and layoffs at Argo AI. Plus from the 5th annual Smart Driving Cars Summit, Anil Lewis of the National Federation of the Blind and ITN America founder Katherine Freund. Join Princeton's Alain Kornhauser and co-host Fred Fishkin for episode 274 of Smart Driving Cars."

Technical support provided by: [https://www.cartsmobility.com/](https://www.cartsmobility.com/)

The SmartDrivingCars eLetter, Pod-Casts, Zoom-Casts and Zoom-inars are made possible in part by support from the Smart Transportation and Technology ETF, symbol MOTO. For more information: [www.motoetf.com](https://www.smartetfs.com/). Most funding is supplied by Princeton University's Department of Operations Research & Financial Engineering and Princeton Autonomous Vehicle Engineering (PAVE) research laboratory as part of its research dissemination initiative

###

### [Two new fatal Tesla crashes are being examined by US investigators](https://www.theverge.com/2022/7/7/23198997/tesla-fatal-crashes-california-florida-autopilot-nhtsa)

A. Hawkins, July, 7, "Two fatal Tesla crashes are being examined by investigators at the National Highway Traffic Safety Administration. Reuters reported that NHTSA opened a special investigation into a recent fatal crash in California, in which a Tesla driver killed a pedestrian. And an agency spokesperson confirmed to The Verge that a crash that took place on July 6th in Florida is also under examination.

The crash in Florida took place on Interstate 75, just south of Gainesville, where a Tesla vehicle smashed into the rear of a stationary tractor-trailer that was parked at a truck stop. Two people inside the Tesla, the driver and a passenger, were killed, according to Fox 35. A spokesperson for NHTSA said the agency was aware of the crash and was currently communicating with Tesla about it.

A spokesperson for the Florida Highway Patrol said it is not known yet whether Autopilot was activated at the time of the crash. ..." [Read more](https://www.theverge.com/2022/7/7/23198997/tesla-fatal-crashes-california-florida-autopilot-nhtsa) Hmmmm... Another crash into a stationary object in the lane ahead. I know that I keep repeating myself, but AV code is structured to track objects by placing on each object a position vector and velocity vector; and even acceleration and jerk and ... vectors.

The problem may well be in how these position vectors include data with respect to how reliably "can I pass underneath the object if I encounter it".

At some point in the code, objects are classed into two buckets... 1. Don't hit these, and 2. Don't worry about these.

Approach velocity (the difference between my car's velocity and the velocity of the object) likely plays an important role in this classification.

For objects "in the lane ahead" one can reliably determine if the object ahead is moving or stationary.

If it is moving, then great.. follow it! If it makes it through, then I'll also make it through, so just follow it and don't rear-end it. (Not that simple, but you get the point).

If it is stationary, oh my goodness, where did that come from? If it was moving, then surely I've been watching it come to rest and no problem, I've been slowing down too. If not, then surely I must be able to pass underneath it. It's just an overpass, or a sign, or traffic light, or tree, or ... that I encounter all the time above my road ahead. No problem! ... I can easily pass under, so just disregard it!

If it is a parked truck... Yipes!!!

If it is moving at me, oh my goodness again; but I see these all the time. Especially on two lane roads that are turning to the right and there is moving traffic in the oncoming lane. Disregard these so you don't start hitting the brakes, because surely we'll somehow pass by each other safely. This one is really tough. If it ever happens that a Tesla, or anyone of these "AVs", is involved in a head-on collision then NHTSA better do a real deep dive into what the system did and didn't do during the whole approach sequence. I suspect that transients of this situation are watched, but quickly disregarded. The question is.. the definition of transient and at what point is it taken seriously. Reliabilities and uncertainties are everything here.

I'm sure the "head-on situation" has been studied in simulation and may well have been studied in an actual demonstration. On a test track, one could send two Teslas towards each other with no one inside either and see what happens. They've probably done that. If so, please let us know what happened. If it hasn't been done, then IIHS or NHTSA should do it. NHTSA and/or IIHS could readily take a Tesla with no one inside and hive it drive down one of its crash testing areas. Have they done that? They should. Should be easier to do than one of their normal crash tests. More importantly, the Tesla should come to rest and no crash happened. Costs them nothing! They must have done that. Sorry to be so stupid here.

Also, I've not heard of a head-on collision of a Tesla vehicle traveling in its lane. When that one occurs, it will be interesting to see how "AutoPilot" handled an object in the lane ahead that was heading towards the Tesla. I've also not heard of a Tesla AutoPilot/FSD successfully avoiding a head-on. It would be great to learn about them, if they exist. Alain

### ['We are killing people': How technology has made your car 'a candy store of distraction'](https://www.latimes.com/business/story/2022-07-06/we-are-killing-people-how-technology-has-made-your-car-a-candy-store-of-distraction)

R. Mitchel, July 6, "In the late 1980s, the U.S. Army turned to outside experts to study how pilots of Apache attack helicopters were responding to the torrent of information streaming into the cockpit on digital screens and analog displays. The verdict: not well.

The cognitive overload caused by all that information was degrading performance and raising the risk of crashes, the researchers determined. Pilots were forced to do too many things at once, with too many bells and whistles demanding their attention. Over the next decade, the Army overhauled its Apache fleet, redesigning cockpits to help operators maintain focus.... " [Read more](https://www.latimes.com/business/story/2022-07-06/we-are-killing-people-how-technology-has-made-your-car-a-candy-store-of-distraction) Hmmmm...Just crazy!! Begin by removing the big screens from the front seat. Alain

### [Waymo autonomous vehicle attacked by an 'erratic' pedestrian in Arizona](https://www.theverge.com/2022/7/7/23198997/tesla-fatal-crashes-california-florida-autopilot-nhtsa)

A. Hawkins, July, 7, "An "erratic" pedestrian attacked a Waymo autonomous vehicle late Tuesday evening in Tempe, Arizona, smashing the windshield and injuring the safety driver, the company said. It was the latest incident of people in Arizona attacking Waymo vehicles — and occasionally their safety drivers — as the company ramps up its [commercial service in the state](https://www.theverge.com/2019/12/9/21000085/waymo-fully-driverless-car-self-driving-ride-hail-service-phoenix-arizona). ..." Read more Hmmmm... And we thought that no one misbehaved in Arizona. Alain

### [Behind the scenes of Waymo's worst automated truck crash](https://techcrunch.com/2022/07/01/behind-the-scenes-of-waymos-worst-automated-truck-crash/)

M. Harris, July 1, "The most serious crash to date involving a self-driving truck might have resulted in only moderate injuries, but it exposed how unprepared local government and law enforcement are to deal with the new technology.

On May 5, a Class 8 Waymo Via truck operating in autonomous mode with a human safety operator behind the wheel was hauling a trailer northbound on Interstate 45 toward Dallas, Texas. At 3:11 p.m., just outside Ennis, the modified Peterbilt was traveling in the far right lane when a passing truck and trailer combo entered its lane.

The driver of the Waymo Via truck told police that the other semi truck continued to maneuver into the lane, forcing Waymo's truck and trailer off the roadway. She was later taken to a hospital for injuries that Waymo described in its report to the National Highway Traffic Safety Administration as "moderate." The other truck drove off without stopping.... " [Read more](https://techcrunch.com/2022/07/01/behind-the-scenes-of-waymos-worst-automated-truck-crash/) Hmmmm... If this is really the "worst automated truck crash" all this stuff is really good! It wasn't even a crash. Slow news month so far. We're even reporting good news. Alain

### [Tesla will open up Superchargers to non-Tesla electric vehicles in the US later this year](https://www.theverge.com/2022/7/7/23198696/tesla-supercharger-non-tesla-ev-us-white-house)

A. Hawkins, July 7, "Tesla plans to open up its Supercharger network to non-Tesla electric vehicles in the US in late 2022, according to a White House memo.

The company has been allowing non-Tesla EVs to use its Supercharger plugs in several cities in Europe as part of a limited pilot program but has been quiet about when US charging stations would be available to non-Tesla EV owners. [A "fact sheet" published by the White House](https://www.whitehouse.gov/briefing-room/statements-releases/2022/06/28/fact-sheet-biden-harris-administration-catalyzes-more-than-700-million-in-private-sector-commitments-to-make-ev-charging-more-affordable-and-accessible/) on June 28th and [noticed by InsideEVs indicates](https://insideevs.com/news/596539/tesla-supercharger-pilot-program-non-tesla-evs-2022/) that those EV owners may be able to use Superchargers as soon as the end of this year.

"Later this year, Tesla will begin production of new Supercharger equipment that will enable non-Tesla EV drivers in North America to use Tesla Superchargers," the White House states. ..." [Read more](https://www.theverge.com/2022/7/7/23198696/tesla-supercharger-non-tesla-ev-us-white-house) Hmmmm... Another revenue opportunity for Elon. Alain

### [Elon Musk's 'Teslas in Tunnels' Las Vegas project is still happening, and here's the first station](https://www.theverge.com/2022/6/30/23190249/boring-company-resorts-world-vegas-loop-station-photos)

A. Hawkins, July 7, "The first passenger station in the "Vegas Loop" network of vehicle tunnels that's being built by Elon Musk's Boring Company was revealed Thursday. The station is situated underneath Resorts World Las Vegas, the first in what is expected to be 55 stops along 29 miles of tunnels.

The Boring Company already operates a small version of this "Teslas in Tunnels" system underneath the Las Vegas Convention Center, which [opened](https://www.theverge.com/2021/5/26/22455365/elon-musk-boring-company-las-vegas-test-lvcc-loop-teslas) in early 2021 and involves two 0.8-mile tunnels. Afterward, Musk's startup proposed [a massive citywide expansion](https://www.theverge.com/2020/12/15/22176596/elon-musk-boring-company-las-vegas-strip-tesla-tunnels) that was eventually approved by Clark County officials last year. The system uses human-controlled Model X and Y vehicles to transport passengers, despite Musk's [previous statements about using sleds](https://www.theverge.com/2018/3/9/17102452/elon-musk-boring-company-pedestrian-cyclist-focus) to carry cars through the tunnels. ..." [Read more](https://www.theverge.com/2022/6/30/23190249/boring-company-resorts-world-vegas-loop-station-photos) Hmmmm... More advances. Alain

Calendar of Upcoming Events

[Garden Grove, CA](https://trb.secure-platform.com/a/page/AutomatedRoadTransportationSymposium) [July 18-21, 2022](https://trb.secure-platform.com/a/page/AutomatedRoadTransportationSymposium)

### Previous SmartDrivingCars [ZoomCast/PodCasts](https://www.youtube.com/watch?v=SNMyGfIAVEo)

These editions are sponsored by the SmartETFs Smart Transportation and Technology ETF, symbol MOTO. For more information head to [www.motoetf.com](https://gate.sc/?url=http://www.motoetf.com&token=314192-1-1579871872239)

[https://www.cartsmobility.com/](https://www.cartsmobility.com/) provided technical support

SmartDrivingCars [ZoomCast Episode 273](https://www.youtube.com/watch?v=SNMyGfIAVEo)/ [PodCast 2](https://anchor.fm/smartdrivingcars/episodes/Smart-Driving-Cars-Episode-268-Why-wireless-EV-charging-is-key-to-autonomous-mobility-e1iimbi) Michael Sena, Editor The Dispatcher

F. Fishkin, June 23, "Smart Driving Cars episode 273: Getting Moves moving. The June Princeton Smart Driving Cars Summit brought the players together. Now the real game begins. "The Dispatcher" publisher and consultant Michael Sena joins us for that plus...Einride's autonomous electric transports, Cruise takes paying passengers and a critical checkpoint for Zoox. " 

SmartDrivingCars [ZoomCast Episode 272](https://www.youtube.com/watch?v=SNMyGfIAVEo)/ [PodCast 2](https://anchor.fm/smartdrivingcars/episodes/Smart-Driving-Cars-episode-273-Getting-Moves-moving-e1kc4f7) Ed Niedermeyer

F. Fishkin, June 16, "With NHTSA releasing the data on 392 crashes involving driver assistance systems, we dive into the significance and take-aways with guest Ed #Niedermeyer, author, journalist and co-host of the #Autonocast. Join Princeton's Alain Kornhauser & co-host Fred Fishkin for episode 272 of Smart Driving Cars."

SmartDrivingCars [ZoomCast Episode 271](https://www.youtube.com/watch?v=oj7QjsR6dL0)/ [PodCast 2](https://anchor.fm/smartdrivingcars/episodes/Smart-Driving-Cars-Episode-268-Why-wireless-EV-charging-is-key-to-autonomous-mobility-e1iimbi) w/ Michael Sena, Publisher of The Dispatcher

F. Fishkin, May 26, "Smart Driving Cars (episode 269) Did government car ratings take a wrong turn? The star rating system for new cars doesn't offer the protections it should. That's the view of consultant and "The Dispatcher" publisher Michael Sena. He joins Alain Kornhauser and Fred Fishkin for episode 269 of Smart Driving Cars. Plus... another self driving promise from Elon Musk, the Smart Driving Cars Summit and more.."

SmartDrivingCars [ZoomCast Episode 268](https://www.youtube.com/watch?v=oj7QjsR6dL0)/ [PodCast 268](https://anchor.fm/smartdrivingcars/episodes/Smart-Driving-Cars-Episode-268-Why-wireless-EV-charging-is-key-to-autonomous-mobility-e1iimbi) w/ Bob Kacergis, CCO, Momentum Dynamics

F. Fishkin, May 15, "Wireless electric vehicle charging can make autonomous mobility services more affordable for all. How? Momentum Dynamics Chief Commercial Officer Bob Kacergis explains on episode 268 of Smart Driving Cars with Princeton's Alain Kornhauser & co-host Fred Fishkin. Plus..Oshkosh, Torc Robotics, Trenton Moves and more."

SmartDrivingCars [ZoomCast Episode 2](https://youtu.be/mJLwot_SfrI)/ [PodCast 267](https://soundcloud.com/smartdrivingcar/smart-driving-cars-episode-267-tesla-autopilot-safety-the-princeton-smart-driving-cars-summit) w/ Michael Sena, Publisher, The Dispatcher

F. Fishkin, March 30, "The latest from the Symposium on the Future Networked Car, the UK investigates laws for driverless cars, cars....politics and Russia, Tesla and some big news from Waymo. The Dispatcher publisher Michael Sena joins Princeton's Alain Kornhauser & co-host Fred Fishkin for Smart Driving Cars episode 262."

SmartDrivingCars [ZoomCast Episode 2](https://youtu.be/NCFqu3WaTh4)/ [PodCast 2](https://anchor.fm/smartdrivingcars/episodes/Smart-Driving-Cars-episode-263-Providing-mobility-to-Ukrainian-refugees-e1gr87c) w/ Henry Posner III'77, Ferroequinalogist

F. Fishkin, April 7, "Mobility takes on a different meaning for Ukrainian refugees. Henry Posner II and his Railroad Development Corporation has been helping to transport many into Germany. He joins Alain Kornhauser and Fred Fishkin for episode 263 of Smart Driving Cars. That plus GM Cruise, Aurora, VW, Qualcomm & more."

SmartDrivingCars [ZoomCast Episode 2](https://www.youtube.com/watch?v=ICjhKHpEe5w)/ [PodCast 2](https://soundcloud.com/smartdrivingcar/smart-driving-cars-episode-264-massive-robotaxi-move-by-musk) w/ Michael Sena, CEO, Uniphy

F. Fishkin, April 23, "Designing the robotaxi rider experience. Uniphy CEO Jim Nicholas is forging partnerships to help transform consumer experiences with vehicles and more. He joins Alain Kornhauser and Fred Fishkin for that...plus the latest on Tesla, Trenton and more."

F. Fishkin, March 3, "How will electric vehicle charging stations make money? The Dispatcher publisher Michael Sena poses that question and many more on episode 258 of Smart Driving Cars with Princeton's Alain Kornhauser and co-host Fred Fishkin. Plus Ford creates a distinct EV car business, an update on NJ progress and more. Tune in and subscribe...."

SmartDrivingCars [ZoomCast Episode 2](https://www.youtube.com/watch) [5](https://www.youtube.com/watch?v=mtQ5jsslqUc) [7](https://www.youtube.com/watch?v=mtQ5jsslqUc) [PodCast 257](https://anchor.fm/smartdrivingcars/episodes/Smart-Driving-Cars-257-Marc-Scribner--Cliff-Winston-e1eu4l9) [Ciff Winston](https://www.brookings.edu/experts/clifford-winston/) Brookings Institute & [Marc Scribner](https://reason.org/author/marc-scribner/) Reason Foundation

F. Fishkin, Feb. 25, "So what about these reports and opinion pieces casting doubt on the future of autonomous mobility? The Brookings Institution's Cliff Winston and Reason Foundation's Marc Scribner join Princeton's Alain Kornhauser & co-host Fred Fishkin to slice and dice. Plus GM Cruise, VW and more.."

SmartDrivingCars [ZoomCast Episode 2](https://www.youtube.com/watch?v=xFegxpeq0Gk) [56](https://www.youtube.com/watch?v=h2vTs6qXNB0) [PodCast 256](https://soundcloud.com/smartdrivingcar/smart-driving-cars-episode-256-with-nvidias-danny-shapiro) w/[Danny Shapiro, VP Automotive, NVIDIA](https://blogs.nvidia.com/blog/author/danny-shapiro/)

F. Fishkin, Feb. 18, "With Jaguar Land Rover signing on to partner with NVIDIA for advanced driver assistance and autonomous capabilities in all of their vehicles starting in 2025, what will the collaboration mean? NVIDIA's VP for Automotive Danny Shapiro joins Princeton's Alain Kornhauser & co-host Fred Fishkin for that plus the latest on Waymo, VW, Trenton and more."

SmartDrivingCars [ZoomCast Episode 2](https://www.youtube.com/watch?v=xFegxpeq0Gk) [PodCast 255](https://soundcloud.com/smartdrivingcar/smart-driving-cars-episode-255) w/[Brad Templeton](https://www.templetons.com/brad/)

F. Fishkin, Feb. 11, "The engaging debate over disengagements. In episode 255 of Smart Driving Cars, Forbes.com Sr. Transportation Contributor Brad Templeton engages with Princeton's Alain Kornhauser over the path to the future of autonomous mobility. The latest data on disengagements from companies testing self driving vehicles in California, Tesla, Cruise, Waymo and New Jersey begins funding Trenton MOVES...are part of the spirited discussion with co-host Fred Fishkin."

SmartDrivingCars [Pod-Cast Episode 254](https://open.spotify.com/episode/1XaAXc0JHiEDMyn4VQOpl3) [Zoom-Cast Episode 2](https://www.youtube.com/watch?v=LGezxqtbyBY)

F. Fishkin, Jan. 27, "The Federal Trade Commission looks to level the tech playing field...but "The Dispatcher" publisher Michael Sena has some words of warning. He joins Princeton's Alain Kornhauser and Fred Fishkin for that plus Tesla, Waymo and more on Episode 253 of Smart Driving Cars.."

SmartDrivingCars [Pod-Cast Episode 252](https://anchor.fm/smartdrivingcars/episodes/Smart-Driving-Cars-Episode-252-IIHS-will-rate-vehicle-partial-automation-systems-e1d7ssd) [Zoom-Cast Episode 2](https://www.youtube.com/watch?v=64fptNGcUFI)

F. Fishkin, Jan. 20, "The IIHS has announced it will rate vehicle partial automation systems. Spearheading is research scientist Alexandra Mueller who joins us. And Professor Emeritus Michael Krauss from the George Mason University School of Law on the manslaughter charges leveled in a Tesla autopilot case in California. Episode 252 of Smart Driving Cars with Princeton's Alain Kornhauser and co-host Fred Fishkin."

SmartDrivingCars [Zoom-Cast Episode 2](https://youtu.be/DT8rmDYzwkg) [51](https://youtu.be/DT8rmDYzwkg)

F. Fishkin, Jan. 15, "In this special edition of Smart Driving Cars, Princeton's Alain Kornhauser and his presentation: [Making it Happen: Trenton Moves-a framework for the deployment of safe, equitable, affordable, sustainable, high quality transportation](https://www.cartsmobility.com/blog/kornhauser-trb-2022). The focus is on providing autonomous mobility in a place where there is real need. A first. Join the effort." [Link to 250 previous SDC PodCasts & ZoomCasts](https://www.dropbox.com/s/y2xlnlaphxb0i6k/Links2PodCast_55-220.pdf?dl=0)

Recent Highlights of:

### 

June 11, 2022 THE DISPATCHER

[Princeton Fifth Annual SmartDrivingCars Summit](http://www.michaellsena.com/wp-content/uploads/2022/06/The-Dispatcher_July_2022.pdf) June 24, M. Sena "THE DISPATCHER, July 2022

IN THIS ISSUE

Princeton Fifth Annual SmartDrivingCars Summit

Safe, Equitable, Affordable, Sustainable, High-quality Mobility for Everyone

Dispatch Central

Someone lit a fire under NHTSA

The Economist: Right analysis, wrong solution

Musings of a Dispatcher: Eyes on the Back Story

The evolution of digital maps and ADAS

Digital Maps for the Vehicle – 1970-2022

" [Read more](http://www.michaellsena.com/wp-content/uploads/2022/06/The-Dispatcher_July_2022.pdf) Hmmmm... Another great edition and very well written summary of the 5th Summit. Alain June 18, 2022

[NHTSA Releases Initial Data on Safety Performance of Advanced Vehicle Technologies](https://www.nhtsa.gov/press-releases/initial-data-release-advanced-vehicle-technologies)

June 15, Press release, "Today, as part of the U.S. Department of Transportation's efforts to increase roadway safety and encourage innovation, the National Highway Traffic Safety Administration [published the initial round of data](https://www.nhtsa.gov/laws-regulations/standing-general-order-crash-reporting) it has collected through its [Standing General Order](https://www.nhtsa.gov/node/103801) issued last year and initial accompanying reports summarizing this data.

The SAE Level 2 advanced driver assistance systems summary report [is available here](https://www.nhtsa.gov/document/summary-report-standing-general-order-adas-l2), while the SAE Levels 3-5 automated driving systems summary report [is available here](https://www.nhtsa.gov/document/summary-report-standing-general-order-ads). Going forward, NHTSA will release data updates monthly..." [Read more](https://www.nhtsa.gov/press-releases/initial-data-release-advanced-vehicle-technologies) Hmmmm... This is a good start; however, as NHTSA repeats many times, this is just a start and there are many "data limitations". The most severe may well be the possibility of substantial "[sampling bias](https://en.wikipedia.org/wiki/Sampling_bias)", the most severe of which is that each OEM sourced the reported data very differently. That makes the data between OEMs incomparable.

Also unreported is any measure that would enable a "crash rate" for an OEM to be determined. One only has a numerator value but no denominator value.

Finally, 392 crashes of "Level 2" cars were reported during the "10" month period of July 2021 and May 15, 2022. About [12 million vehicles are involved in traffic crashes](https://www.statista.com/topics/3708/road-accidents-in-the-us/#topicHeader__wrapper) every year among the 283 million vehicles that operate in the US. Assuming any one vehicle is unlikely to be involved in more than one crash per year, it means that each vehicle, on average is involved in 12M/283M = 0.0424 crashes per year. Thus, if these ADAS cars were involved in crashes at the average rate, and had their ADAS on all the time, the 500 vehicle crashes per year contained in these data would expect to be generated from a fleet of only about 11,800 vehicles (or 0.0042% of the vehicles ("everything being equal", ADAS on all the time.).

Consequently, either, ...

* These systems outrageously reduce crash probabilities, and/or

* maybe some, but we're probably not much luckier.

* very few of the cars in use during that "10" month period had Level 2 capabilities, and/or

* unfortunately, the VIN number doesn't identify these cars and only Tesla announces how many sold (I may have missed the reportings)

* very few of the drivers of those cars rarely engaged the Level 2 features, and/or

* likely. Only Tesla releases data on the utilization of its level 2 features but does so only in aggregate terms that don't allow for correction of sampling bias associated with engagement in "easy" driving conditions versus "challenging" driving conditions.

* enormous undercounting

* likely, only Tesla has the opportunity to either "know all" or sample effectively because of their [OtA monitoring](https://www.wired.com/insights/2014/02/teslas-air-fix-best-example-yet-internet-things/) of its vehicles. Everyone else has conveniently kept their heads in the sand. Mercedes didn't report any; however, during that period I think my Intelligent Cruise Control and Lane Centering were engaged when I hit a deer. Mercedes must not have been watching me, I didn't report it and I didn't get the memo that informed me to do anything.

Anyway. It is a start and at least to me the numbers are not startling.

What needs improvement is sourcing of the incidents. Maybe OtA should be mandated. At minimum, the VIN should specify the existence of these capabilities. Then normal police reportings can begin to "automatically" access the "[black box event recorders](https://en.wikipedia.org/wiki/Event_data_recorder)" (see also [Accident data recorder](https://en.wikipedia.org/wiki/Accident_data_recorder) and [NHTSA](https://www.nhtsa.gov/research-data/event-data-recorder) that are in most cars today. Unfortunately, [privacy concerns](https://www.ncsl.org/research/telecommunications-and-information-technology/privacy-of-data-from-event-data-recorders.aspx) makes this not-easy. So here we are. It won't be easy to do much better, but we should continue to try.

What the data do point out is that a substantial number of the crashes involved the rear-ending of a stationary object. I have pointed out repeatedly that the source code of these systems explicitly disregard stationary objects in the lane ahead. Justifying this explicit process is that current sensors incur unacceptable false positives when trying to determine if sufficient headroom exists under detected stationary objects in the lane ahead. Thus, to avoid braking in response to these rare false positives, stationary objects in the lane ahead are all assumed to be "pass under-able".

As one drives, one encounters many stationary objects in the lane ahead. These are readily sensed and precisely located ahead. Readily sensed are overpasses, signs, tree canopies, traffic lights, ... all of which can usually be readily passed under. (As can vehicles ahead that come to rest in vehicle-follower mode. These are not disregarded because one is in vehicle-follower mode.)

But when one is in vehicle-leader mode and one encounters a stationary object ahead, I believe, most, if not all "Level 2" systems disregard that object and assume the car can pass underneath. So if you are in vehicle leader mode and come over the crest of a hill to be confronted with a stopped object ahead, your system will disregard that object. Similarly, if the vehicle that you are following changes lanes forcing you to become a leader, any stationary object ahead will be disregarded. Alain

June 11, 2022

3 minute Promo: [https://youtu.be/q5Ov_dPuRV4](https://youtu.be/q5Ov_dPuRV4)

The 5th Summit: [https://www.cartsmobility.com/summit](https://www.cartsmobility.com/summit)

[Summit Preview Tour](https://images.squarespace-cdn.com/content/v1/614ac4ef54d1aa1941cc4a60/f3abf253-396d-46cf-bb8b-14b664c073ee/SmartDrivingCars-Summit-Preview-FinalFinal.jpg?format=1000w)

[Dr. Steve Still's Tribute to Heywood Patterson](https://vimeo.com/716226813/1927a6fb4b)

S. Still, June 3, "... Heywood Patterson, 67, He often drove members of his church to Tops, helping them load their groceries into his car and then taking them home. "That's what he did all the time," Deborah Patterson said. "That's what he loved to do". ..." [Watch Video](https://vimeo.com/716226813/1927a6fb4b) Hmmmm... A principal reason for "Trenton MOVES"-like deployments is to do what Heywood Patterson "loved to do" for the many. Alain May 28, 2022

[The Evolving Business of Powering Our Vehicles](http://www.michaellsena.com/wp-content/uploads/2022/05/The-Dispatcher_June_2022.pdf)

M. Sena, May 24, "New Car Assessment Programs (NCAPs) all around the world have created a separate and unequal set of standards for vehicle safety operating in parallel with the Type Approval processes in most countries and the U.S. Federal Motor Vehicle Safety Standards and their equivalents in other countries. One standard is enough. In this month's lead article, I look at why this has happened, why it is not a good idea, and what should be done to correct the situation.

There is no Musings in this month's issue. Instead, I have put my musings energies to work in Dispatch Central. You can see the topics below. The section ends with a notable quote from the CEO of Stellantis on the topic of battery electric vehicles.

Enjoy your June issue of The Dispatcher. All comments are welcome, whether you want to take exception to something I have written or you just want to let me know that you got something out of reading it. ..." [Read more](https://www.forbes.com/sites/bradtempleton/2022/05/11/waymo-cruise-chinese-firms-expand-robotaxi-service-areas-its-on/) Hmmmm... Every month, great reading. Enjoy! Alain May 15, 2022

[From pricing carbon to fighting opioid abuse, ORFE showcased top senior projects](https://engineering.princeton.edu/news/2022/05/11/pricing-carbon-fighting-opioid-abuse-orfe-showcased-top-senior-projects) A. Nathans, May 11, "When Serena Ren presented her senior thesis on using machine learning for art appraisals last month, she hoped to see her friend, Joyce Luo, present her thesis on fighting opioid addiction. But since all students in the Department of Operations Research and Financial Engineering present their theses in parallel sessions, this was impossible.

But on May 4, Ren and Luo finally got to see each other's presentations in a classroom in Sherrerd Hall, thanks to the department's first-ever event in which selected students present their thesis work to the whole department.... " [Read more](https://engineering.princeton.edu/news/2022/05/11/pricing-carbon-fighting-opioid-abuse-orfe-showcased-top-senior-projects) Hmmmm... I'm so proud! Hopefully we'll be able to release the video so you can enjoy. Keep trying the link:

[Princeton ORFE Class of 2022 Senior Thesis Symposium "Best 8"](https://youtu.be/RlrHnI5qvA0)

* Isabelle Grosgogeat "[Impact of women and minority ownership on private equity](https://www.youtube.com/watch?v=RlrHnI5qvA0&t=20s)"

* Joyce Luo "[Equitable data-driven resource allocation to fight the opioid pandemic](https://youtu.be/RlrHnI5qvA0?t=1184)"

* Caroline Noonan "[The impact of carbon price on power plant dispatch, production costs, and total emissions](https://youtu.be/RlrHnI5qvA0?t=1903)"

* Hari Ramakrishnan "[Lighting up dark pools](https://youtu.be/RlrHnI5qvA0?t=3026)"

* Serena Ren "[Automatic art appraisals](https://youtu.be/RlrHnI5qvA0?t=3967)"

* Mitchell Stroebell "[A comparison of advanced player statistics for the NBA](https://youtu.be/RlrHnI5qvA0?t=4827)"

* Jack Woll  
"[Pairs trading and volatility](https://youtu.be/RlrHnI5qvA0?t=5673)"

* Andre Yin  
"[Equity trading strategies based on macroeconomic event analysis](https://youtu.be/RlrHnI5qvA0?t=6650)"

May 7, 2022  

[PAVE VIRTUAL PANEL "AVS AND PUBLIC GOOD: TRENTON MOVES"](https://pavecampaign.org/event/avs-and-public-good-trenton-moves-2/)

PAVE,  
May 4,  
"Autonomous vehicle technologies offer incredible potential: they could make our highways safer, they could offer new mobility options for people who can't drive, and they could help create a more equitable transportation system for those who are not well-served by our current system.  

During the month of May, we are highlighting places where AVs are in use — today — being deployed, tested, and used for public good. We want to look at examples of the technology being used to serve food deserts, to expand access to rural communities, to offer new accessibility options, and more.  

We are starting with the Trenton MOVES initiative, which is the first large-scale urban transit system in America based entirely on self-driving shuttles. The shuttles, which carry four to eight passengers, serve traditionally underserved Trenton neighborhoods, where 70% of households have limited access to a single automobile, or no access at all. Our panelists will detail the program, describing how it works, the results it has achieved, and their vision for the future......"  
[Read more](https://pavecampaign.org/event/avs-and-public-good-trenton-moves-2/)  

Hmmmm...  
Very nice. Be sure to [watch video](https://youtu.be/KawGghbte4s) 😁 and see [ZoomCast 267](https://youtu.be/mJLwot_SfrI?t=1137) Alain  

April 30, 2022  

[NJDOT Commissioner Gutierrez-Scaccetti and the Trenton NJ MOVES Program](https://allenovery.podbean.com/e/propel-njdot-commissioner-gutierrez-scaccetti-and-the-trenton-nj-moves-program/)  

P. Keller, April 29, "New Jersey recently announced a $5 million grant for the Trenton Mobility & Opportunity: Vehicles Equity System or MOVES Project. The grant to the City of Trenton will support the planned start up and eventual deployment of 100 Autonomous Vehicles that will provide an on-demand automated transit system to serve the 90,000 residents of Trenton....."  
[Read more](https://allenovery.podbean.com/e/propel-njdot-commissioner-gutierrez-scaccetti-and-the-trenton-nj-moves-program/)  

Hmmmm...  
Very nice. 😁  
April 23, 2022  

[Knight Foundation](https://twitter.com/knightfdn)  
April 21, "CARTS Executive Director Jerry He explains to the audience at [#CoMotionMiami](https://twitter.com/hashtag/CoMotionMiami?src=hashtag_click) that:  

Hmmmm...  
Yup! [See ZoomCast265](https://youtu.be/BrJCfkNtCxM?t=2786) Alain  

April 15, 2022  

[Musk promises 'dedicated robotaxi' with futuristic look from Tesla](https://www.reuters.com/business/autos-transportation/tesla-open-texas-factory-critical-growth-ambitions-2022-04-07/)  
H. Jin, April 6, "Electric carmaker Tesla (TSLA.O) will make a "dedicated" self-driving taxi that will "look futuristic," Chief Executive Elon Musk said on Thursday, without giving a timeframe.  

The 50-year-old billionaire, wearing a black cowboy hat and sunglasses, made the comments at the opening of Tesla's $1.1 billion factory in Texas, which is home to its new headquarters.  

"Massive scale. Full self-driving. There's going to be a dedicated robotaxi," Musk told a large crowd at the factory...."  
[Read more](https://www.reuters.com/business/autos-transportation/tesla-open-texas-factory-critical-growth-ambitions-2022-04-07/)  

Hmmmm... Wow! It was brilliant for Elon to begin focusing his EVs on rich Californians who already have a stable full of cars to go all the way to grandma's house and back and were really looking for a neat toy.  

Elon followed the graceful rollout of his Supercharger infrastructure which enabled the upper-middle class that doesn't have a backup fleet and needs to have a toy and reliably go back and forth to grandma's house. Viola!!! No longer just a toy. Seamless evolution to "[Massive Scale](https://www.reuters.com/business/autos-transportation/tesla-open-texas-factory-critical-growth-ambitions-2022-04-07/)" scale and Massive Profitability.  

RoboTaxis' evolution to "[Massive Scale](https://www.reuters.com/business/autos-transportation/tesla-open-texas-factory-critical-growth-ambitions-2022-04-07/)" is turning out to be different. Starting with rich WesternStaters doesn't seem to be working sociologically for Waymo. The rides offered seem to be taken for entertainment and side-show purposes rather than valued enablers of enhanced quality of life. Nice for selfies, but not much more.  

Recall fundamental value is to provide a safe, high-quality ride from A to B. "Safe" is "safe", but "high-quality" is relative to what one now has readily available. For the rich, that's where they've already put a lot of money to create for themselves something really nice. The chances someone is going to offer something better to an individual that has crafted something perfect for themselves is slim-to-none. Consequently, the service is used primarily for taking selfies.  

For those that don't have their own car for whatever reason (can't drive, don't want to, too young, too old, and/or too poor) their mobility options are simply dreadful. Absolutely trivial for aTaxi service to be viewed as the quality winner and used to provide customer accessibility, improved quality of life, endearment, respect, love, appreciation, loyalty, and use.  

Consequently, if Elon is really serious about achieving "[Massive Scale](https://www.reuters.com/business/autos-transportation/tesla-open-texas-factory-critical-growth-ambitions-2022-04-07/)" then he should basically flip his Tesla strategy and start by focusing on serving the mobility needs of those that will fully appreciate and gain the most personal value from his market offering;  

* those that don't already have a stable full of their own personal mobility options.  

* those for which his aTaxi can substantially change their lives for the better.  

These are the customers of [Trenton MOVES](https://www.cartsmobility.com/blog/kornhauser-trb-2022); only about 50,000 of Trenton's 90,000 population; but 50,000 that will really appreciate you. Start by only serving Trenton's 8 square mile area with about 100 vehicles and only during the best 350 days out of the year's 365.25.  

They'll be so appreciative and you will have provided the spark that will allow your aTaxis to go viral! You'll quickly serve Mercer county, Newark, Camden, Atlantic City, New Brunswick, Toms River, Perth Amboy, all of New Jersey, Eastern Pennsylvania, New York City (except Manhattan), Long Island, .....  

That's the natural road to "[Massive Scale](https://www.reuters.com/business/autos-transportation/tesla-open-texas-factory-critical-growth-ambitions-2022-04-07/)" for Mobility for all. Start with those in most need and evolve to convert those that will leave their own cars parked in their driveway.  

"[Massive Scale](https://www.reuters.com/business/autos-transportation/tesla-open-texas-factory-critical-growth-ambitions-2022-04-07/)" starts with [Trenton MOVES](https://www.cartsmobility.com/blog/kornhauser-trb-2022). Alain  

March 31, 2022  

[Taking our next step in the City by the Bay](https://blog.waymo.com/2022/03/taking-our-next-step-in-city-by-bay.html?m=1)  
The Waymo Team, March 30, "This morning in San Francisco, a fully autonomous all-electric Jaguar I-PACE, with no human driver behind the wheel, picked up a Waymo engineer to get their morning coffee and go to work. Since sharing that we were ready to take the next step and begin testing fully autonomous operations in the city, we've begun fully autonomous rides with our San Francisco employees. They now join the thousands of Waymo One riders we've been serving in Arizona, making fully autonomous driving technology part of their daily lives...."  
[Read more](https://blog.waymo.com/2022/03/taking-our-next-step-in-city-by-bay.html?m=1)  

Hmmmm... Congratulations! Enormous accomplishment and fundamental expression of confidence in your technology. Please come to New Jersey where we are certain that you can actually deliver "Safe, Equitable, Affordable, Sustainable, High-quality Mobility" that will substantially improve the quality-of-life of many by transforming affordable housing into affordable living and more.  

Let's look at the back-of-the-envelope numbers...  

Trenton:  

Population: 90,000.  
PersonTrips/Day (non-walking): 300,000  
IntraTrenton: 150,000  
PersonTripLength (90%tile): 10 miles  
intraTrenton (100%tile) 5 miles  

Operational Productivity:  
VehicleTrips/Day: 50  
Average Vehicle Occupancy (AVO): 2  
PersonTrips/VehicleDay: 100  
PersonTrips/VehicleYear: 35,000  

100 vehicle fleet productivity: 10,000 PersonTrips/day (1/15th market penetration)  

50% market penetration Fleet requirements: 500 vehicles (AVO =2.5) for 60 PersonTrips/VehicleDay).  

Cost:  
Depreciation/PersonTrip @ $200k/vehicle, 4 year life = $200,000/(4*35,000) = $10/7 = $1.43/PersonTrip  
Electricity + maintenance + management + ... = $0.57/PersonTrip  
Cost = $2.00/PersonTrip  

New Jersey:  

Population: 9+ Million  

PersonTrips/Day (non-walking): >30 Million  

IntraNJ + NJT/Septa to/from NYC & PHL: 30 Million  
PersonTripLength (90%tile): 10 miles  
Operational Productivity  
VehicleTrips/Day: 60  
Average Vehicle Occupancy (AVO): 2.5  
PersonTrips/VehicleDay: 150  
PersonTrips/VehicleYear: 50,000  

10% market penetration (3 Million PersonTrips/Day: Fleet requirements: 20,000 vehicles (AVO =2.5) for 60 PersonTrips/VehicleDay).  

Cost:  
Depreciation/PersonTrip @ $200k/vehicle, 4 year life = 200,000/(4*35,000)= $10/7 = $1.43  
Electricity + maintenance + management ... = $0.57  
Cost per PersonTrip = $2.00  
Revenue: (10% market penetration: 3M personTrips/Day)  

10% @ cost + 90% market pricing:  

10% @ $2.00/PersonTrip (300,000*$2.00 = $600,000/day; $200M/year  
90% @ $3.70/personTrip (2.7M*3.70 = $10M/day; 3.5B/year (value proposition could have the average market price even higher than $3.70/personTrip (+$1.70 over cost)  

Profit: $1.70 *2.7M = $4.6M/day = $1.5B/year  

Seems to me that Waymo should have responded to the NJ DoT RfEI and shouldn't be completely ignoring me. I guess I'm missing something. Maybe someone else will call me? 😎 Alain  

[Moving Forward with Trenton MOVES](https://viodi.com/2022/02/09/moving-forward-with-trenton-moves/)  
K. Pyle, Feb. 9, "Dr. Alain Kornhauser's vision of bringing equitable, sustainable, and affordable mobility to the people of Trenton took another step forward with the February 9th, 2022 announcement (Facebook) of a $5 million NJDOT Local Transportation Planning Fund Grant for the Trenton Mobility & Opportunity: Vehicles Equity System (MOVES) Project (PDF). The significance of this event goes beyond the grant announcement..."  
[Read more](https://viodi.com/2022/02/09/moving-forward-with-trenton-moves/)  

Hmmmm... Ken, thank you for the kind words. Alain  

[Smart Driving Cars Extra: Trenton MOVES gets moving](https://www.youtube.com/watch?v=GXnluyz2GSE)  

Feb. 11, "The New Jersey DOT is providing 5 million dollars to get Trenton MOVES moving. The goal..autonomous, affordable, safe mobility for all. This is a video of the event held on February 9th."  
[Read more](https://www.youtube.com/watch?v=GXnluyz2GSE)  

Hmmmm... Fantastic even with challenging audio. Turn on Closed Caption. The substance is in the quality of the words from the Mayor, Commissioner and Superintendent. All from the heart. Very worth absorbing. Alain.  

February 4, 2022  
[Trenton MOVES](https://www.dropbox.com/s/kxyvrjqi1u351tj/TretonHS_Announcenet_Invitation.pdf?dl=0)  
W. Skaggs, Feb. 3,"We are excited to invite you to join Mayor Gusciora, N.J. Department of Transportation (NJDOT) Commissioner Diane Gutierrez-Scaccetti, and Trenton Public Schools Superintendent James Earle to celebrate a $5 million award from the NJDOT Local Transportation Projects Fund for an unprecedented public transportation project right here in the Capital City. The project is called the Trenton Mobility & Opportunity: Vehicular Equity System (MOVES) initiative.  

Originally [announced by Governor Murphy and Commissioner Gutierrez-Scaccetti in December](https://www.nj.gov/governor/news/news/562021/approved/20211206b.shtml#:~:text=Trenton%20MOVES%20will%20act%20to,serve%2090%2C000%20residents%20of%20Trenton.) TrentonMOVES seeks to provide a safe, equitable, and affordable high-quality on-demand mobility service to Trenton residents. The effort is a collaboration between the Governor's Office, NJDOT, the City of Trenton, and Princeton University.  

The $5 million award is a huge milestone for the project. This will be the first large-scale urban transit system in America to be based entirely on self-driving shuttles. Each vehicle will carry four to eight passengers at a time. The AVs will be low-cost to users in underserved neighborhoods. The high school will be one of the central destinations on the first routes.  

The event will take place at 11:00 a.m. on in the Trenton Central High School auditorium. Members of the press will be invited to attend. ...."  
[Read more](https://www.dropbox.com/s/kxyvrjqi1u351tj/TretonHS_Announcenet_Invitation.pdf?dl=0)  

Hmmmm... Another real milestone.  

The Trenton MOVES RfEI closed February 25, with 20 submittals. Next comes the [5th Princeton SmartDrivingCar Summit](https://www.cartsmobility.com/summit) June 2 -> 4, 2022 in Princeton & Trenton, NJ. The Summit will be focused on enabling Trentonians to get a first glimpse at technology and mobility systems that can deliver Trenton MOVES' mobility objectives (Safety, Equity, Affordability, Sustainability,..) and, very importantly, enabling technology and mobility companies to learn the market opportunities available to be captured in Trenton, the rest of Mercer County, and throughout New Jersey.  

Trenton MOVES is a win-win opportunity for the citizens of New Jersey (The Public) and the shareholders of mobility provider(s) (The Private), who can come together in a Trenton MOVES Public-Private-Partnership (PPP) that will be created through a Request for Proposal (RfP) process commencing shortly after the close of the Summit. 😁 Alain  

###  

Alain L. Kornhauser, PhD  

Professor, Operations Research & Financial Engineering  

Director of Undergraduate Studies, ORFE  

Director, Transportation Program  

Faculty Chair, Princeton Autonomous Vehicle Engineering  

229 Sherrerd Hall  

Princeton University  

Princeton, NJ  

[alaink@princeton.edu](mailto:alaink@princeton.edu)  

609-980-1427 (c)  