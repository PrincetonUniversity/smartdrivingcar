---
layout: newsletter
title: "Wednesday, Feb. 9, 2022"
date: 2022-02-09
permalink: /10.22-NHTSA_ADAS_Data-061822/
display_name: "10.22 - Nhtsa_Adas_Data 061822"
---
SmartDrivingCars eLetter

### [NHTSA Releases Initial Data on Safety Performance of Advanced Vehicle Technologies](https://www.nhtsa.gov/press-releases/initial-data-release-advanced-vehicle-technologies)

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

What the data do point out is that a substantial number of the crashes involved the rear-ending of a stationary object. I have pointed out repeatedly that the source code of these systems explicitly disregard stationary objects in the lane ahead. Justifying this explicit process is that current sensors incur unacceptable false positives when trying to determine if sufficient headroom exists under detected stationary object in the lane ahead. Thus, to avoid braking in response to these rare false positives, stationary objects in the lane ahead are all assumed to be "pass under-able".

As one drives, one encounters many stationary objects in the lane ahead. These are readily sensed and precisely located ahead. Readily sensed are overpasses, signs, tree canopies, traffic lights, ... all of which can usually be readily passed under. (As can vehicles ahead that come to rest in vehicle-follower mode. These are not disregarded because one is in vehicle-follower mode.)

But when one is in vehicle-leader mode and one encounters a stationary object ahead, I believe, most, if not all "Level 2" systems disregard that object and assume the car can pass underneath. So if you are in vehicle leader mode and come over the crest of a hill to be confronted with a stopped object ahead, your system will disregard that object. Similarly, if the vehicle that you are following changes lanes forcing you to become a leader, any stationary object ahead will be disregarded. Alain

### SmartDrivingCars [ZoomCast Episode 272](https://www.youtube.com/watch?v=SNMyGfIAVEo)/ [PodCast 2](https://anchor.fm/smartdrivingcars/episodes/Smart-Driving-Cars-Episode-268-Why-wireless-EV-charging-is-key-to-autonomous-mobility-e1iimbi) Ed Niedermeyer

F. Fishkin, June 16, "With NHTSA releasing the data on 392 crashes involving driver assistance systems, we dive into the significance and take-aways with guest Ed Niedermeyer, author, journalist and co-host of the Autonocast. Join Princeton's Alain Kornhauser & co-host Fred Fishkin for episode 272 of Smart Driving Cars."

Technical support provided by: [https://www.cartsmobility.com](https://www.cartsmobility.com)

### [Taking a Closer Look at the NHTSA ADAS Crash Data](https://www.cartsmobility.com/blog/nhtsa-adas-crash-data)

G. Laniewsky, June 17, "Plotting Each Crash on a Map We created an interactive map that shows where each accident happened and some relevant information. Tesla Autopilot is colored in red, every other manufacturer is in blue. ..." [Read more](https://www.cartsmobility.com/blog/nhtsa-adas-crash-data) Hmmmm... just the beginning of our look at the data. Alain

### [Most driver-assist crashes involved Teslas, new data show. But questions abound](https://www.latimes.com/business/story/2022-06-15/tesla-autopilot-crash-report-nhtsa)

R. Mitchell, June 15, "... But far more detail and context are required before regulators can say definitively whether such systems can outperform human drivers, or one another.

"The data may raise more questions than they answer," NHTSA head Steven Cliff told reporters...." [Read more](https://www.cartsmobility.com/blog/nhtsa-adas-crash-data) Hmmmm... This is a beginning. While there is still a lot we don't know, we know a lot more today than we knew before the release. Alain

### [Self-driving cars crash, too, but figuring out what it means requires much better data](https://www.theverge.com/2022/6/16/23169960/nhtsa-adas-av-crash-data-standardize)

A. Hawkins, June 16, "This week, for the first time ever, the National Highway Traffic Safety Administration released data on crashes involving cars equipped with advanced driver-assist systems and automated driving technology. A lot of headlines — including The Verge's — focused on the number of Tesla vehicles that crashed, which is understandable because Tesla had a lot of crashes.

But the numbers themselves don't tell us the whole story. In fact, they don't really tell us much of any story at all. Not yet..." [Read more](https://www.theverge.com/2022/6/16/23169960/nhtsa-adas-av-crash-data-standardize) Hmmmm... Yup. Alain

### [US releases new driver-assist crash data, and surprise, it's mostly Tesla](https://www.theverge.com/2022/6/15/23168088/nhtsa-adas-self-driving-crash-data-tesla)

A. Hawkins, June 15, ".The federal government released two new reports highlighting — for the first time — crashes and fatalities involving autonomous vehicles (AV) and vehicles equipped with advanced driver-assist systems (ADAS). Tesla reported the most crashes involving driver-assist technology, while Alphabet's Waymo disclosed the most incidents involving its autonomous vehicles.

Car and tech companies insist these technologies save lives, but more people died in auto crashes last year than in the last three decades. More data is needed to accurately determine whether these new systems are making roads safer or simply making driving more convenient.." [Read more](https://www.theverge.com/2022/6/15/23168088/nhtsa-adas-self-driving-crash-data-tesla) Hmmmm... Yup. Alain

### [Tesla Autopilot and Other Driver-Assist Systems Linked to Hundreds of Crashes](https://www.nytimes.com/2022/06/15/business/self-driving-car-nhtsa-crash-data.html)

N. Boudette, June 15, "..." [Read more](https://www.nytimes.com/2022/06/15/business/self-driving-car-nhtsa-crash-data.html) Hmmmm... The article is fine, but the headline is a non-subtle and unfair dig at Tesla and the whole sector. True, the data set was restricted to Driver-Assist Systems and reported Crashes. Consequently, these two terms are "linked".

And hundreds were involved, but the tabloid-styled wording of the headline is insulting to the image of the "back in the day" NY Times.

If the authors wished to provide a quantitative measure for the linkage, they should have put their measure in some perspective, like ... in the US there are roughly 12 million vehicles annually involved in road crashes. They could then have stated "... linked to 0.0042% of crashes" Just as accurate, much different inference by many. [C'mon NY Times!!!](https://www.youtube.com/watch?v=moNbAjylenQ) Alain

### [California's first commercial robotaxi is approved for the streets of San Francisco](https://www.latimes.com/business/story/2022-06-02/californias-first-commercial-robotaxi-service-approved-for-san-francisco)

R. Mitchell, June 2, ".Robotaxis are now a real thing in California.

On Thursday, state officials green-flagged the launch of a fare-based ride-hailing business featuring cars with no human driver at the wheel.

Robot-operated Chevy Bolt EVs will be rolled out over the next few weeks by autonomous vehicle maker Cruise. The San Francisco company, owned by General Motors, wouldn't say how many.

With a permit from the California Public Utilities Commission, Cruise becomes the first commercial robotaxi business in the state and the second in the U.S. The first was launched in 2020 by Alphabet-owned Waymo in Chandler, Ariz....." [Read more](https://www.latimes.com/business/story/2022-06-02/californias-first-commercial-robotaxi-service-approved-for-san-francisco) Hmmmm... Congratulations Kyle, Mo, Carter, ... Time now to come do the same in Trenton. Thank you for actively participating in the [5th Summit](https://www.cartsmobility.com/summit).😁 Alain

### [Ferrari Will Stick With Level 2 Autonomy to Preserve the Driving Experience](https://www.cnet.com/roadshow/news/ferrari-level-2-semi-autonomy-adas/?TheTime=2022-06-16T22:24:38&UniqueID=1BBEB346-EDC3-11EC-893B-ECBC923C408C&PostType=link&ftag=COS-05-10aaa0b&ServiceType=twitter)

A. Krok, June 16, "Will the ever-increasing glut of advanced driver-assistance systems eventually claim supercars? Is there even room for exotica in a world full of sensors and onboard artificial intelligence? Ferrari sure seems to think there is.

Ferrari on Thursday unveiled its strategic plan for from now until 2026. While it's mighty impressive that the Italian automaker intends to unveil 15 new cars over the next several years, including a hypercar and a battery-electric vehicle, it's the mention of conditional autonomy that might be of interest to some.

"Ferrari will limit the autonomy of its cars to Level 2/Level 2 Plus, in order to preserve all the extraordinary emotions reserved for the driver," the company said in its press release. Level 2 and Level 2 Plus include ADAS arrays that are capable of controlling the car in certain conditions, but they still require the driver's full attention. ... [Read more](https://www.cnet.com/roadshow/news/ferrari-level-2-semi-autonomy-adas/?TheTime=2022-06-16T22:24:38&UniqueID=1BBEB346-EDC3-11EC-893B-ECBC923C408C&PostType=link&ftag=COS-05-10aaa0b&ServiceType=twitter) Hmmmm... Not at all surprising. So will every other OEM including "[Yugo](https://www.caranddriver.com/features/a21082360/a-quick-history-of-the-yugo-the-worst-car-in-history/)." As I wrote many years ago and still believe.. No way "the ultimate driving machine", becomes "the ultimate riding machine". Alain

Calendar of Upcoming Events

[Garden Grove, CA](https://trb.secure-platform.com/a/page/AutomatedRoadTransportationSymposium) [July 18-21, 2022](https://trb.secure-platform.com/a/page/AutomatedRoadTransportationSymposium)

[https://cdn.filestackcontent.com/f6IjIRUR5SAGGJfQuFfA?Participating%20Companies%20Logos.pdf](https://cdn.filestackcontent.com/f6IjIRUR5SAGGJfQuFfA?Participating%20Companies%20Logos.pdf)

These editions are sponsored by the SmartETFs Smart Transportation and Technology ETF, symbol MOTO. For more information head to [www.motoetf.com](https://www.motoetf.com)

### [Taking a Closer Look at the NHTSA ADAS Crash Data](https://www.cartsmobility.com/blog/nhtsa-adas-crash-data)

G. Laniewsky, June 17, "Plotting Each Crash on a Map We created an interactive map that shows where each accident happened and some relevant information. Tesla Autopilot is colored in red, every other manufacturer is in blue. ..." [Read more](https://www.cartsmobility.com/blog/nhtsa-adas-crash-data) Hmmmm... just the beginning of our look at the data. Alain

### [Most driver-assist crashes involved Teslas, new data show. But questions abound](https://www.latimes.com/business/story/2022-06-15/tesla-autopilot-crash-report-nhtsa)

R. Mitchell, June 15, "... But far more detail and context are required before regulators can say definitively whether such systems can outperform human drivers, or one another.

"The data may raise more questions than they answer," NHTSA head Steven Cliff told reporters...." [Read more](https://www.cartsmobility.com/blog/nhtsa-adas-crash-data) Hmmmm... This is a beginning. While there is still a lot we don't know, we know a lot more today than we knew before the release. Alain

### [Self-driving cars crash, too, but figuring out what it means requires much better data](https://www.theverge.com/2022/6/16/23169960/nhtsa-adas-av-crash-data-standardize)

A. Hawkins, June 16, "This week, for the first time ever, the National Highway Traffic Safety Administration released data on crashes involving cars equipped with advanced driver-assist systems and automated driving technology. A lot of headlines — including The Verge's — focused on the number of Tesla vehicles that crashed, which is understandable because Tesla had a lot of crashes.

But the numbers themselves don't tell us the whole story. In fact, they don't really tell us much of any story at all. Not yet..." [Read more](https://www.theverge.com/2022/6/16/23169960/nhtsa-adas-av-crash-data-standardize) Hmmmm... Yup. Alain

### [US releases new driver-assist crash data, and surprise, it's mostly Tesla](https://www.theverge.com/2022/6/15/23168088/nhtsa-adas-self-driving-crash-data-tesla)

A. Hawkins, June 15, ".The federal government released two new reports highlighting — for the first time — crashes and fatalities involving autonomous vehicles (AV) and vehicles equipped with advanced driver-assist systems (ADAS). Tesla reported the most crashes involving driver-assist technology, while Alphabet's Waymo disclosed the most incidents involving its autonomous vehicles.

Car and tech companies insist these technologies save lives, but more people died in auto crashes last year than in the last three decades. More data is needed to accurately determine whether these new systems are making roads safer or simply making driving more convenient.." [Read more](https://www.theverge.com/2022/6/15/23168088/nhtsa-adas-self-driving-crash-data-tesla) Hmmmm... Yup. Alain

### [Tesla Autopilot and Other Driver-Assist Systems Linked to Hundreds of Crashes](https://www.nytimes.com/2022/06/15/business/self-driving-car-nhtsa-crash-data.html)

N. Boudette, June 15, "..." [Read more](https://www.nytimes.com/2022/06/15/business/self-driving-car-nhtsa-crash-data.html) Hmmmm... The article is fine, but the headline is a non-subtle and unfair dig at Tesla and the whole sector. True, the data set was restricted to Driver-Assist Systems and reported Crashes. Consequently, these two terms are "linked".

And hundreds were involved, but the tabloid-styled wording of the headline is insulting to the image of the "back in the day" NY Times.

If the authors wished to provide a quantitative measure for the linkage, they should have put their measure in some perspective, like ... in the US there are roughly 12 million vehicles annually involved in road crashes. They could then have stated "... linked to 0.0042% of crashes" Just as accurate, much different inference by many. [C'mon NY Times!!!](https://www.youtube.com/watch?v=moNbAjylenQ) Alain

### [California's first commercial robotaxi is approved for the streets of San Francisco](https://www.latimes.com/business/story/2022-06-02/californias-first-commercial-robotaxi-service-approved-for-san-francisco)

R. Mitchell, June 2, ".Robotaxis are now a real thing in California.

On Thursday, state officials green-flagged the launch of a fare-based ride-hailing business featuring cars with no human driver at the wheel.

Robot-operated Chevy Bolt EVs will be rolled out over the next few weeks by autonomous vehicle maker Cruise. The San Francisco company, owned by General Motors, wouldn't say how many.

With a permit from the California Public Utilities Commission, Cruise becomes the first commercial robotaxi business in the state and the second in the U.S. The first was launched in 2020 by Alphabet-owned Waymo in Chandler, Ariz....." [Read more](https://www.latimes.com/business/story/2022-06-02/californias-first-commercial-robotaxi-service-approved-for-san-francisco) Hmmmm... Congratulations Kyle, Mo, Carter, ... Time now to come do the same in Trenton. Thank you for actively participating in the [5th Summit](https://www.cartsmobility.com/summit).😁 Alain

### [Ferrari Will Stick With Level 2 Autonomy to Preserve the Driving Experience](https://www.cnet.com/roadshow/news/ferrari-level-2-semi-autonomy-adas/?TheTime=2022-06-16T22:24:38&UniqueID=1BBEB346-EDC3-11EC-893B-ECBC923C408C&PostType=link&ftag=COS-05-10aaa0b&ServiceType=twitter)

A. Krok, June 16, "Will the ever-increasing glut of advanced driver-assistance systems eventually claim supercars? Is there even room for exotica in a world full of sensors and onboard artificial intelligence? Ferrari sure seems to think there is.

Ferrari on Thursday unveiled its strategic plan for from now until 2026. While it's mighty impressive that the Italian automaker intends to unveil 15 new cars over the next several years, including a hypercar and a battery-electric vehicle, it's the mention of conditional autonomy that might be of interest to some.

"Ferrari will limit the autonomy of its cars to Level 2/Level 2 Plus, in order to preserve all the extraordinary emotions reserved for the driver," the company said in its press release. Level 2 and Level 2 Plus include ADAS arrays that are capable of controlling the car in certain conditions, but they still require the driver's full attention. ... [Read more](https://www.cnet.com/roadshow/news/ferrari-level-2-semi-autonomy-adas/?TheTime=2022-06-16T22:24:38&UniqueID=1BBEB346-EDC3-11EC-893B-ECBC923C408C&PostType=link&ftag=COS-05-10aaa0b&ServiceType=twitter) Hmmmm... Not at all surprising. So will every other OEM including "[Yugo](https://www.caranddriver.com/features/a21082360/a-quick-history-of-the-yugo-the-worst-car-in-history/)." As I wrote many years ago and still believe.. No way "the ultimate driving machine", becomes "the ultimate riding machine". Alain

Calendar of Upcoming Events

[Garden Grove, CA](https://trb.secure-platform.com/a/page/AutomatedRoadTransportationSymposium) [July 18-21, 2022](https://trb.secure-platform.com/a/page/AutomatedRoadTransportationSymposium)

[https://cdn.filestackcontent.com/f6IjIRUR5SAGGJfQuFfA?Participating%20Companies%20Logos.pdf](https://cdn.filestackcontent.com/f6IjIRUR5SAGGJfQuFfA?Participating%20Companies%20Logos.pdf)

These editions are sponsored by the SmartETFs Smart Transportation and Technology ETF, symbol MOTO. For more information head to [www.motoetf.com](https://www.motoetf.com)

### [Taking a Closer Look at the NHTSA ADAS Crash Data](https://www.cartsmobility.com/blog/nhtsa-adas-crash-data)

G. Laniewsky, June 17, "Plotting Each Crash on a Map We created an interactive map that shows where each accident happened and some relevant information. Tesla Autopilot is colored in red, every other manufacturer is in blue. ..." [Read more](https://www.cartsmobility.com/blog/nhtsa-adas-crash-data) Hmmmm... just the beginning of our look at the data. Alain

### [Most driver-assist crashes involved Teslas, new data show. But questions abound](https://www.latimes.com/business/story/2022-06-15/tesla-autopilot-crash-report-nhtsa)

R. Mitchell, June 15, "... But far more detail and context are required before regulators can say definitively whether such systems can outperform human drivers, or one another.

"The data may raise more questions than they answer," NHTSA head Steven Cliff told reporters...." [Read more](https://www.cartsmobility.com/blog/nhtsa-adas-crash-data) Hmmmm... This is a beginning. While there is still a lot we don't know, we know a lot more today than we knew before the release. Alain

### [Self-driving cars crash, too, but figuring out what it means requires much better data](https://www.theverge.com/2022/6/16/23169960/nhtsa-adas-av-crash-data-standardize)

A. Hawkins, June 16, "This week, for the first time ever, the National Highway Traffic Safety Administration released data on crashes involving cars equipped with advanced driver-assist systems and automated driving technology. A lot of headlines — including The Verge's — focused on the number of Tesla vehicles that crashed, which is understandable because Tesla had a lot of crashes.

But the numbers themselves don't tell us the whole story. In fact, they don't really tell us much of any story at all. Not yet..." [Read more](https://www.theverge.com/2022/6/16/23169960/nhtsa-adas-av-crash-data-standardize) Hmmmm... Yup. Alain

### [US releases new driver-assist crash data, and surprise, it's mostly Tesla](https://www.theverge.com/2022/6/15/23168088/nhtsa-adas-self-driving-crash-data-tesla)

A. Hawkins, June 15, ".The federal government released two new reports highlighting — for the first time — crashes and fatalities involving autonomous vehicles (AV) and vehicles equipped with advanced driver-assist systems (ADAS). Tesla reported the most crashes involving driver-assist technology, while Alphabet's Waymo disclosed the most incidents involving its autonomous vehicles.

Car and tech companies insist these technologies save lives, but more people died in auto crashes last year than in the last three decades. More data is needed to accurately determine whether these new systems are making roads safer or simply making driving more convenient.." [Read more](https://www.theverge.com/2022/6/15/23168088/nhtsa-adas-self-driving-crash-data-tesla) Hmmmm... Yup. Alain

### [Tesla Autopilot and Other Driver-Assist Systems Linked to Hundreds of Crashes](https://www.nytimes.com/2022/06/15/business/self-driving-car-nhtsa-crash-data.html)

N. Boudette, June 15, "..." [Read more](https://www.nytimes.com/2022/06/15/business/self-driving-car-nhtsa-crash-data.html) Hmmmm... The article is fine, but the headline is a non-subtle and unfair dig at Tesla and the whole sector. True, the data set was restricted to Driver-Assist Systems and reported Crashes. Consequently, these two terms are "linked".

And hundreds were involved, but the tabloid-styled wording of the headline is insulting to the image of the "back in the day" NY Times.

If the authors wished to provide a quantitative measure for the linkage, they should have put their measure in some perspective, like ... in the US there are roughly 12 million vehicles annually involved in road crashes. They could then have stated "... linked to 0.0042% of crashes" Just as accurate, much different inference by many. [C'mon NY Times!!!](https://www.youtube.com/watch?v=moNbAjylenQ) Alain

### [California's first commercial robotaxi is approved for the streets of San Francisco](https://www.latimes.com/business/story/2022-06-02/californias-first-commercial-robotaxi-service-approved-for-san-francisco)

R. Mitchell, June 2, ".Robotaxis are now a real thing in California.

On Thursday, state officials green-flagged the launch of a fare-based ride-hailing business featuring cars with no human driver at the wheel.

Robot-operated Chevy Bolt EVs will be rolled out over the next few weeks by autonomous vehicle maker Cruise. The San Francisco company, owned by General Motors, wouldn't say how many.

With a permit from the California Public Utilities Commission, Cruise becomes the first commercial robotaxi business in the state and the second in the U.S. The first was launched in 2020 by Alphabet-owned Waymo in Chandler, Ariz....." [Read more](https://www.latimes.com/business/story/2022-06-02/californias-first-commercial-robotaxi-service-approved-for-san-francisco) Hmmmm... Congratulations Kyle, Mo, Carter, ... Time now to come do the same in Trenton. Thank you for actively participating in the [5th Summit](https://www.cartsmobility.com/summit).😁 Alain

### [Ferrari Will Stick With Level 2 Autonomy to Preserve the Driving Experience](https://www.cnet.com/roadshow/news/ferrari-level-2-semi-autonomy-adas/?TheTime=2022-06-16T22:24:38&UniqueID=1BBEB346-EDC3-11EC-893B-ECBC923C408C&PostType=link&ftag=COS-05-10aaa0b&ServiceType=twitter)

A. Krok, June 16, "Will the ever-increasing glut of advanced driver-assistance systems eventually claim supercars? Is there even room for exotica in a world full of sensors and onboard artificial intelligence? Ferrari sure seems to think there is.

Ferrari on Thursday unveiled its strategic plan for from now until 2026. While it's mighty impressive that the Italian automaker intends to unveil 15 new cars over the next several years, including a hypercar and a battery-electric vehicle, it's the mention of conditional autonomy that might be of interest to some.

"Ferrari will limit the autonomy of its cars to Level 2/Level 2 Plus, in order to preserve all the extraordinary emotions reserved for the driver," the company said in its press release. Level 2 and Level 2 Plus include ADAS arrays that are capable of controlling the car in certain conditions, but they still require the driver's full attention. ... [Read more](https://www.cnet.com/roadshow/news/ferrari-level-2-semi-autonomy-adas/?TheTime=2022-06-16T22:24:38&UniqueID=1BBEB346-EDC3-11EC-893B-ECBC923C408C&PostType=link&ftag=COS-05-10aaa0b&ServiceType=twitter) Hmmmm... Not at all surprising. So will every other OEM including "[Yugo](https://www.caranddriver.com/features/a21082360/a-quick-history-of-the-yugo-the-worst-car-in-history/)." As I wrote many years ago and still believe.. No way "the ultimate driving machine", becomes "the ultimate riding machine". Alain

Calendar of Upcoming Events

[Garden Grove, CA](https://trb.secure-platform.com/a/page/AutomatedRoadTransportationSymposium) [July 18-21, 2022](https://trb.secure-platform.com/a/page/AutomatedRoadTransportationSymposium)

[https://cdn.filestackcontent.com/f6IjIRUR5SAGGJfQuFfA?Participating%20Companies%20Logos.pdf](https://cdn.filestackcontent.com/f6IjIRUR5SAGGJfQuFfA?Participating%20Companies%20Logos.pdf)

These editions are sponsored by the SmartETFs Smart Transportation and Technology ETF, symbol MOTO. For more information head to [www.motoetf.com](https://www.motoetf.com)

SmartDrivingCars [ZoomCast Episode 2](https://www.youtube.com/watch?v=xFegxpeq0Gk) [56](https://www.youtube.com/watch?v=h2vTs6qXNB0) / [PodCast 256](https://soundcloud.com/smartdrivingcar/smart-driving-cars-episode-256-with-nvidias-danny-shapiro) w/[Danny Shapiro, VP Automotive, NVIDIA](https://blogs.nvidia.com/blog/author/danny-shapiro/)

F. Fishkin, Feb. 18, "With Jaguar Land Rover signing on to partner with NVIDIA for advanced driver assistance and autonomous capabilities in all of their vehicles starting in 2025, what will the collaboration mean? NVIDIA's VP for Automotive Danny Shapiro joins Princeton's Alain Kornhauser & co-host Fred Fishkin for that plus the latest on Waymo, VW, Trenton and more."

SmartDrivingCars [ZoomCast Episode 2](https://www.youtube.com/watch?v=xFegxpeq0Gk) [55](https://www.youtube.com/watch?v=NFMNxU0616A) / [PodCast 255](https://soundcloud.com/smartdrivingcar/smart-driving-cars-episode-255) w/[Brad Templeton](https://www.templetons.com/brad/)

F. Fishkin, Feb. 11, "The engaging debate over disengagements. In episode 255 of Smart Driving Cars, Forbes.com Sr. Transportation Contributor Brad Templeton engages with Princeton's Alain Kornhauser over the path to the future of autonomous mobility. The latest data on disengagements from companies testing self driving vehicles in California, Tesla, Cruise, Waymo and New Jersey begins funding Trenton MOVES...are part of the spirited discussion with co-host Fred Fishkin."

SmartDrivingCars [Pod-Cast Episode 254](https://open.spotify.com/episode/1XaAXc0JHiEDMyn4VQOpl3) [Zoom-Cast Episode 2](https://www.youtube.com/watch?v=LGezxqtbyBY) [5](https://www.youtube.com/watch?v=LGezxqtbyBY) w/Alex Roy

###

F. Fishkin, Feb 4, "Why Self Driving Isn't a Race, It's a Game. That's what Alex Roy, Director of Special Projects at Argo AI writes at [www.groundtruthautonomy.com](http://www.groundtruthautonomy.com). Alex joins Princeton's Alain Kornhauser and co-host Fred Fishkin for the latest Smart Driving Cars for a wide ranging discussion on that plus the latest on Trenton Moves, FreightWaves, Tesla, Waymo, Cruise, Toyota and more."

SmartDrivingCars [Pod-Cast Episode 253](https://anchor.fm/smartdrivingcars/episodes/Smart-Driving-Cars-Episode-253-e1dhsgu) [Zoom-Cast Episode 2](https://www.youtube.com/watch?v=64fptNGcUFI) [5](https://www.youtube.com/watch?v=64fptNGcUFI) w/Michael Sena, Editor of The Dispatcher

###

F. Fishkin, Jan. 27, "The Federal Trade Commission looks to level the tech playing field...but "The Dispatcher" publisher Michael Sena has some words of warning. He joins Princeton's Alain Kornhauser and Fred Fishkin for that plus Tesla, Waymo and more on Episode 253 of Smart Driving Cars.."

SmartDrivingCars [Pod-Cast Episode 252](https://anchor.fm/smartdrivingcars/episodes/Smart-Driving-Cars-Episode-252-IIHS-will-rate-vehicle-partial-automation-systems-e1d7ssd) [Zoom-Cast Episode 2](https://www.youtube.com/watch?v=64fptNGcUFI) [5](https://www.youtube.com/watch?v=64fptNGcUFI) /[Michael Krauss](https://www.law.gmu.edu/faculty/directory/emeritus/krauss_michael), Prof. of Law Emeritus & [Alexandra Mueller](https://www.youtube.com/watch?v=8wJOqjm1hLw), IIHS

F. Fishkin, Jan. 20, "The IIHS has announced it will rate vehicle partial automation systems. Spearheading is research scientist Alexandra Mueller who joins us. And Professor Emeritus Michael Krauss from the George Mason University School of Law on the manslaughter charges leveled in a Tesla autopilot case in California. Episode 252 of Smart Driving Cars with Princeton's Alain Kornhauser and co-host Fred Fishkin."

SmartDrivingCars [Zoom-Cast Episode 2](https://www.youtube.com/watch?v=xFegxpeq0Gk) [51](https://youtu.be/DT8rmDYzwkg) /A. Kornhauser: Making it Happen: Trenton MOVES... a Framework for...

F. Fishkin, Jan. 15, "In this special edition of Smart Driving Cars, Princeton's Alain Kornhauser and his presentation: [Making it Happen: Trenton Moves-a framework for the deployment of safe, equitable, affordable, sustainable, high quality transportation](https://www.cartsmobility.com/blog/kornhauser-trb-2022). The focus is on providing autonomous mobility in a place where there is real need. A first. Join the effort."

[Link to 250 previous SDC PodCasts & ZoomCasts](https://www.dropbox.com/s/y2xlnlaphxb0i6k/Links2PodCast_55-220.pdf?dl=0)

Recent Highlights of:

### 

June 11, 2022

### [3 minute Promo:](https://youtu.be/q5Ov_dPuRV4)

The 5th Summit: [https://www.cartsmobility.com/summit](https://www.cartsmobility.com/summit)

[Summit Preview Tour](https://images.squarespace-cdn.com/content/v1/614ac4ef54d1aa1941cc4a60/f3abf253-396d-46cf-bb8b-14b664c073ee/SmartDrivingCars-Summit-Preview-FinalFinal.jpg?format=1000w)

[Dr. Steve Still's Tribute to Heywood Patterson](https://vimeo.com/716226813/1927a6fb4b)

S. Still, June 3, "... Heywood Patterson, 67, He often drove members of his church to Tops, helping them load their groceries into his car and then taking them home. "That's what he did all the time," Deborah Patterson said. "That's what he loved to do." ... [Watch Video](https://vimeo.com/716226813/1927a6fb4b)

Hmmmm... A principal reason for "Trenton MOVES"-like deployments is to do what Heywood Patterson "loved to do" for the many. Alain May 28, 2022

[The Evolving Business of Powering Our Vehicles](http://www.michaellsena.com/wp-content/uploads/2022/05/The-Dispatcher_June_2022.pdf)

M. Sena, May 24, "New Car Assessment Programs (NCAPs) all around the world have created a separate and unequal set of standards for vehicle safety operating in parallel with the Type Approval processes in most countries and the U.S. Federal Motor Vehicle Safety Standards and their equivalents in other countries. One standard is enough. In this month's the lead article, I look at why this has happened, why it is not a good idea, and what should be done to correct the situation.

There is no Musings in this month's issue. Instead, I have put my musings energies to work in Dispatch Central. You can see the topics below. The section ends with a notable quote from the CEO of Stellantis on the topic of battery electric vehicles.

Enjoy your June issue of The Dispatcher. All comments are welcome, whether you want to take exception to something I have written or you just want to let me know that you got something out of reading it. ... [Read more](http://www.michaellsena.com/wp-content/uploads/2022/05/The-Dispatcher_June_2022.pdf)

Hmmmm... Every month, great reading. Enjoy! Alain May 15, 2022

[From pricing carbon to fighting opioid abuse, ORFE showcased top senior projects](https://engineering.princeton.edu/news/2022/05/11/pricing-carbon-fighting-opioid-abuse-orfe-showcased-top-senior-projects)

A. Nathans, May 11, "When Serena Ren presented her senior thesis on using machine learning for art appraisals last month, she hoped to see her friend, Joyce Luo, present her thesis on fighting opioid addiction. But since all students in the Department of Operations Research and Financial Engineering present their theses in parallel sessions, this was impossible.

But on May 4, Ren and Luo finally got to see each other's presentations in a classroom in Sherrerd Hall, thanks to the department's first-ever event in which selected students present their thesis work to the whole department.... " [Read more](https://engineering.princeton.edu/news/2022/05/11/pricing-carbon-fighting-opioid-abuse-orfe-showcased-top-senior-projects)

Hmmmm... I'm so proud! Hopefully we'll be able to release the video so you can enjoy. Keep trying the link:

[Princeton ORFE Class of 2022 Senior Thesis Symposium "Best 8"](https://youtu.be/RlrHnI5qvA0)

* Isabelle Grosgogeat "[Impact of women and minority ownership on private equity](https://www.youtube.com/watch?v=RlrHnI5qvA0&t=20s)"

* Joyce Luo "[Equitable data-driven resource allocation to fight the opioid pandemic](https://youtu.be/RlrHnI5qvA0?t=1184)"

* Caroline Noonan "[The impact of carbon price on power plant dispatch, production costs, and total emissions](https://youtu.be/RlrHnI5qvA0?t=1903)"

* Hari Ramakrishnan "[Lighting up dark pools](https://youtu.be/RlrHnI5qvA0?t=3026)"

* Serena Ren "[Automatic art appraisals](https://youtu.be/RlrHnI5qvA0?t=3967)"

* Mitchell Stroebell "[A comparison of advanced player statistics for the NBA](https://youtu.be/RlrHnI5qvA0?t=4827)"

* Jack Woll "[Pairs trading and volatility](https://youtu.be/RlrHnI5qvA0?t=5673)"

* Andre Yin "[Equity trading strategies based on macroeconomic event analysis](https://youtu.be/RlrHnI5qvA0?t=6650)"

May 7, 2022

[PAVE VIRTUAL PANEL "AVS AND PUBLIC GOOD: TRENTON MOVES"](https://pavecampaign.org/event/avs-and-public-good-trenton-moves-2/)

PAVE, May 4, "Autonomous vehicle technologies offer incredible potential: they could make our highways safer, they could offer new mobility options for people who can't drive, and they could help create a more equitable transportation system for those who are not well-served by our current system.

During the month of May, we are highlighting places where AVs are in use — today — being deployed, tested, and used for public good. We want to look at examples of the technology being used to serve food deserts, to expand access to rural communities, to offer new accessibility options, and more.

We are starting with the Trenton MOVES initiative, which is the first large-scale urban transit system in America based entirely on self-driving shuttles. The shuttles, which carry four to eight passengers, serve traditionally underserved Trenton neighborhoods, where 70% of households have limited access to a single automobile, or no access at all. Our panelists will detail the program, describing how it works, the results it has achieved, and their vision for the future......" [Read more](https://pavecampaign.org/event/avs-and-public-good-trenton-moves-2/)

Hmmmm... Very nice. Be sure to [watch video](https://youtu.be/KawGghbte4s) 😁 and see [ZoomCast 267](https://youtu.be/mJLwot_SfrI?t=1137) Alain

April 30, 2022

[NJDOT Commissioner Gutierrez-Scaccetti and the Trenton NJ MOVES Program](https://allenovery.podbean.com/e/propel-njdot-commissioner-gutierrez-scaccetti-and-the-trenton-nj-moves-program/)

P. Keller, April 29, "New Jersey recently announced a $5 million grant for the Trenton Mobility & Opportunity: Vehicles Equity System or MOVES Project. The grant to the City of Trenton will support the planned start up and eventual deployment of 100 Autonomous Vehicles that will provide an on-demand automated transit system to serve the 90,000 residents of Trenton....." [Read more](https://allenovery.podbean.com/e/propel-njdot-commissioner-gutierrez-scaccetti-and-the-trenton-nj-moves-program/)

Hmmmm... Very nice. 😁

April 23, 2022

[Knight Foundation](https://twitter.com/knightfdn) April 21, "CARTS Executive Director Jerry He explains to the audience at [#CoMotionMiami](https://twitter.com/hashtag/CoMotionMiami?src=hashtag_click) that:

Hmmmm... Yup! [See ZoomCast 265](https://youtu.be/BrJCfkNtCxM?t=2786) Alain

April 15, 2022

[Musk promises 'dedicated robotaxi' with futuristic look from Tesla](https://www.reuters.com/business/autos-transportation/tesla-open-texas-factory-critical-growth-ambitions-2022-04-07)

H. Jin, April 6, "Electric carmaker Tesla (TSLA.O) will make a "dedicated" self-driving taxi that will "look futuristic," Chief Executive Elon Musk said on Thursday, without giving a timeframe.

The 50-year-old billionaire, wearing a black cowboy hat and sunglasses, made the comments at the opening of Tesla's $1.1 billion factory in Texas, which is home to its new headquarters.

"Massive scale. Full self-driving. There's going to be a dedicated robotaxi," Musk told a large crowd at the factory...." [Read more](https://www.reuters.com/business/autos-transportation/tesla-open-texas-factory-critical-growth-ambitions-2022-04-07)

Hmmmm... Wow! It was brilliant for Elon to begin focusing his EVs on rich Californians who already have a stable full of cars to go all the way to grandma's house and back and were really looking for a neat toy.

Elon followed the graceful rollout of his Supercharger infrastructure which enabled the upper-middle class that doesn't have a backup fleet and needs to have a toy and reliably go back and forth to grandma's house. Viola!!! No longer just a toy. Seamless evolution to "[Massive Scale](https://www.reuters.com/business/autos-transportation/tesla-open-texas-factory-critical-growth-ambitions-2022-04-07)" scale and Massive Profitability.

RoboTaxis' evolution to "[Massive Scale](https://www.reuters.com/business/autos-transportation/tesla-open-texas-factory-critical-growth-ambitions-2022-04-07)" is turning out to be different. Starting with rich WesternStaters doesn't seem to be working sociologically for Waymo. The rides offered seem to be taken for entertainment and side-show purposes rather than valued enablers of enhanced quality of life. Nice for selfies, but not much more.

Recall fundamental value is to provide a safe, high-quality ride from A to B. "Safe" is "safe", but "high-quality" is relative to what one now has readily available. For the rich, that's where they've already put a lot of money to create for themselves something really nice. The chances someone is going to offer something better to an individual that has crafted something perfect for themselves is slim-to-none. Consequently, the service is used primarily for taking selfies.

For those that don't have their own car for whatever reason (can't drive, don't want to, too young, too old, and/or too poor) their mobility options are simply dreadful. Absolutely trivial for an aTaxi service to be viewed as the quality winner and used to provide customer accessibility, improved quality of life, endearment, respect, love, appreciation, loyalty, and use.

Consequently, if Elon is really serious about achieving "[Massive Scale](https://www.reuters.com/business/autos-transportation/tesla-open-texas-factory-critical-growth-ambitions-2022-04-07)" then he should basically flip his Tesla strategy and start by focusing on serving the mobility needs of those that will fully appreciate and gain the most personal value from his market offering;

* those that don't already have a stable full of their own personal mobility options.

* those for which his aTaxi can substantially change their lives for the better.

These are the customers of [Trenton MOVES](https://www.cartsmobility.com/blog/kornhauser-trb-2022); only about 50,000 of Trenton's 90,000 population; but 50,000 that will really appreciate you. Start by only serving Trenton's 8 square mile area with about 100 vehicles and only during the best 350 days out of the year's 365.25.

They'll be so appreciative and you will have provided the spark that will allow your aTaxis to go viral! You'll quickly serve Mercer county, Newark, Camden, Atlantic City, New Brunswick, Toms River, Perth Amboy, all of New Jersey, Eastern Pennsylvania, New York City (except Manhattan), Long Island, .....

That's the natural road to "[Massive Scale](https://www.reuters.com/business/autos-transportation/tesla-open-texas-factory-critical-growth-ambitions-2022-04-07)" for Mobility for all. Start with those in most need and evolve to convert those that will leave their own cars parked in their driveway.

"[Massive Scale](https://www.reuters.com/business/autos-transportation/tesla-open-texas-factory-critical-growth-ambitions-2022-04-07)" starts with [Trenton MOVES](https://www.cartsmobility.com/blog/kornhauser-trb-2022). Alain

March 31, 2022

[Taking our next step in the City by the Bay](https://blog.waymo.com/2022/03/taking-our-next-step-in-city-by-bay.html)

The Waymo Team, March 30, "This morning in San Francisco, a fully autonomous all-electric Jaguar I-PACE, with no human driver behind the wheel, picked up a Waymo engineer to get their morning coffee and go to work. Since sharing that we were ready to take the next step and begin testing fully autonomous operations in the city, we've begun fully autonomous rides with our San Francisco employees. They now join the thousands of Waymo One riders we've been serving in Arizona, making fully autonomous driving technology part of their daily lives...." [Read more](https://blog.waymo.com/2022/03/taking-our-next-step-in-city-by-bay.html)

Hmmmm... Congratulations! Enormous accomplishment and fundamental expression of confidence in your technology. Please come to New Jersey where we are certain that you can actually deliver "Safe, Equitable, Affordable, Sustainable, High-quality Mobility" that will substantially improve the quality of life of many by transforming affordable housing into affordable living and more.

Let's look at the back-of-the-envelope numbers...

Trenton:

Population: 90,000.  
Person Trips/Day (non-walking): 300,000  
Intra Trenton: 150,000  
Person Trip Length (90%tile): 10 miles  
intra Trenton (100%tile) 5 miles  

Operational Productivity:  
Vehicle Trips/Day: 50  
Average Vehicle Occupancy (AVO): 2  
Person Trips/Vehicle Day: 100  
Person Trips/Vehicle Year: 35,000  

100 vehicle fleet productivity: 10,000 Person Trips/day (1/15th market penetration)  

50% market penetration Fleet requirements: 500 vehicles (AVO = 2.5) for 60 Person Trips/Vehicle Day).  

Cost:  
Depreciation/Person Trip @ $200k/vehicle, 4 year life = $200,000/(4*35,000) = $10/7 = $1.43/Person Trip  
Electricity + maintenance + management + ... = $0.57/Person Trip  
Cost = $2.00/Person Trip  

New Jersey:

Population: 9+ Million  

Person Trips/Day (non-walking): >30 Million  

Intra NJ + NJT/Septa to/from NYC & PHL: 30 Million  
Person Trip Length (90%tile): 10 miles  
Operational Productivity  
Vehicle Trips/Day: 60  
Average Vehicle Occupancy (AVO): 2.5  
Person Trips/Vehicle Day: 150  
Person Trips/Vehicle Year: 50,000  

10% market penetration (3 Million Person Trips/Day: Fleet requirements: 20,000 vehicles (AVO = 2.5) for 60 Person Trips/Vehicle Day).  

Cost:  
Depreciation/Person Trip @ $200k/vehicle, 4 year life = 200,000/(4*35,000)= $10/7 = $1.43  
Electricity + maintenance + management ... = $0.57  
Cost per Person Trip = $2.00  
Revenue: (10% market penetration: 3M person Trips/Day)  

10% @ cost + 90% market pricing:  

10% @ $2.00/Person Trip (300,000*$2.00 = $600,000/day; $200M/year  
90% @ $3.70/person Trip (2.7M*3.70 = $10M/day; 3.5B/year (value proposition could have the average market price even higher than $3.70/person Trip (+$1.70 over cost)  

Profit: $1.70 * 2.7M = $4.6M/day = $1.5B/year  

Seems to me that Waymo should have responded to the NJ DoT RfEI and shouldn't be completely ignoring me. I guess I'm missing something. Maybe someone else will call me? 😎 Alain  

[Moving Forward with Trenton MOVES](https://viodi.com/2022/02/09/moving-forward-with-trenton-moves/)  

K. Pyle, Feb. 9, "Dr. Alain Kornhauser's vision of bringing equitable, sustainable, and affordable mobility to the people of Trenton took another step forward with the February 9th, 2022 announcement (Facebook) of a $5 million NJDOT Local Transportation Planning Fund Grant for the Trenton Mobility & Opportunity: Vehicles Equity System (MOVES) Project (PDF). The significance of this event goes beyond the grant announcement..." [Read more](https://viodi.com/2022/02/09/moving-forward-with-trenton-moves/) Hmmmm... Ken, thank you for the kind words. Alain  

[Smart Driving Cars Extra: Trenton MOVES gets moving](https://www.youtube.com/watch?v=GXnluyz2GSE)  

Feb. 11, "The New Jersey DOT is providing 5 million dollars to get Trenton MOVES moving. The goal..autonomous, affordable, safe mobility for all. This is a video of the event held on February 9th." [Read more](https://www.youtube.com/watch?v=GXnluyz2GSE) Hmmmm... Fantastic even with challenging audio. Turn on Closed Caption. The substance is in the quality of the words from the Mayor, Commissioner and Superintendent. All from the heart. Very worth absorbing. Alain. February 4, 2022  

[Trenton MOVES](https://www.dropbox.com/s/kxyvrjqi1u351tj/TretonHS_Announcenet_Invitation.pdf?dl=0)  

W. Skaggs, Feb. 3,"We are excited to invite you to join Mayor Gusciora, N.J. Department of Transportation (NJDOT) Commissioner Diane Gutierrez-Scaccetti, and Trenton Public Schools Superintendent James Earle to celebrate a $5 million award from the NJDOT Local Transportation Projects Fund for an unprecedented public transportation project right here in the Capital City. The project is called the Trenton Mobility & Opportunity: Vehicular Equity System (MOVES) initiative.  

Originally [announced by Governor Murphy and Commissioner Gutierrez-Scaccetti in December](https://www.nj.gov/governor/news/news/562021/approved/20211206b.shtml#:~:text=Trenton%20MOVES%20will%20act%20to,serve%2090,000%20residents%20of%20Trenton.), Trenton MOVES seeks to provide a safe, equitable, and affordable high-quality on-demand mobility service to Trenton residents. The effort is a collaboration between the Governor's Office, NJDOT, the City of Trenton, and Princeton University.  

The $5 million award is a huge milestone for the project. This will be the first large-scale urban transit system in America to be based entirely on self-driving shuttles. Each vehicle will carry four to eight passengers at a time. The AVs will be low-cost to users in underserved neighborhoods. The high school will be one of the central destinations on the first routes.  

The event will take place at 11:00 a.m. in the Trenton Central High School auditorium. Members of the press will be invited to attend. ...." [Read more](https://www.dropbox.com/s/kxyvrjqi1u351tj/TretonHS_Announcenet_Invitation.pdf?dl=0) Hmmmm... Another real milestone.  

The Trenton MOVES RfEI closed February 25, with 20 submittals. Next comes the [5th Princeton Smart Driving Car Summit](https://www.cartsmobility.com/summit) June 2 -> 4, 2022 in Princeton & Trenton, NJ. The Summit will be focused on enabling Trentonians to get a first glimpse at technology and mobility systems that can deliver Trenton MOVES' mobility objectives (Safety, Equity, Affordability, Sustainability,..) and, very importantly, enabling technology and mobility companies to learn the market opportunities available to be captured in Trenton, the rest of Mercer County, and throughout New Jersey.  

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

alaink@princeton.edu  

609-980-1427 (c)  

This list is maintained by [Alain Kornhauser](mailto:alaink@princeton.edu) and hosted by the [Princeton University LISTSERV](http://lists.princeton.edu).