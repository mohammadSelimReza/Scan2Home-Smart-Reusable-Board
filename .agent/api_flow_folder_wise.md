Collection Name: Scan2Home API
=========================================================================================
Parent Folder 1: User
Sub Folder 1 : Login (Login api, Registration API, Refresh Token API, google sign in api, apple sign in api)

Sub Folder 2: Forget Password ( Send OTP API, OTP verify API, New Password Reset API)

Sub Folder 3: Home Screen (All Property Listing API, Favourite add/remove api, Property Filtering API type wise(query param),search/matching property api)

Sub Folder 4: Property details(Full details of property API, Request for schedule api, make offer api , Agent Information API, Rating API,Similar properties api)

Sub Folder 5: Search
all property listing api  with filtering option (price range,property type,amenities,text based search) , add to fav /remove api

Sub Folder 6: QR Search
Scan QR to see property details API

Sub Folder 7: Favorite 
Added Favorite list api , remove from favorite api

Sub Folder 8: Account Settings
User Dashboard API (total fav Properties count,total offer sent count)
Profile Get API
Profile Update API
Password Change API
Delete user account API (using Post request accepting "delete" param)
Terms and Conditions Get API
Privacy and Policy Get API
Send Admin for support and help API


Sub Folder 9: Chat Screen

Chat with AI API




=========================================================================================

Parent Folder 2: Agent

Sub Folder 1: Login (Login api, Registration API, Refresh Token API)

Sub Folder 2: Forget Password

Sub Folder 3: Home Screen
Agent Dashboard API (Total listing count, total views of all listed properties count, total offers of all listed properties count,total qr scanned on agent's listed properties count)
Recent Activity API (title, info,time:2hour ago)


Sub Folder 4: All Property
(All Property Listing API, Favourite add/remove api, Property Filtering API type wise(query param),search/matching property api)

Sub Folder 5: Add Property

Add new property API (images,title,type,price,address,key features((bedroom count,bathroom count,size,parking slot count,pool,garage,garden,fireplace,smart home,gym)),upload video, lon/lat for google map location,)

Add Preview API to temp seeing the property 

Save Property API

Generate QR API (save with it too) 

Download that generate QR API

Sub Folder 6: Offers and Leads

All offer by buyers API
Action api (accept offer /reject offer/add to leads/counter offer)
on counter offer action clicked, Create Counter API with history

Sub Folder 7: My Properties 
List of all properties added by agent (with status:pending/approved/rejected)
Edit property API
Delete property API

Sub Folder 8: Agency Profile
Agency Profile Get API
Agency Profile Update API
Password Change API
Delete agency account API (using Post request accepting "delete" param)
Terms and Conditions Get API
Privacy and Policy Get API
Send Admin for support and help API

Sub Folder 9: Chat Screen
Chat with AI API

Sub Folder 10: Notification API


=========================================================================================
Parent Folder 2: Admin

Sub Folder 1: Login (Login api, Refresh Token API)

Sub Folder 2: Forget Password

Sub Folder 3: Dashboard
Admin Dashboard API (total agent count, total agent active count, total agent pending verification count ,total property listed count on full site,total users, total property views count on whole platform)

Sub Folder 4: Property Management
All property list API ( filter by status (all,approved, rejected), filer by types (house, apartment, vilals,)serch using text based charact )
Pending property post API (approved, reject, view details)

Sub Folder 5: User Management
User list API (full name,email,status,role,join data,last active,action(view/banned)) [pagination]

Sub Folder 6: Agent Management
Agent list API (agent name,agency/company name,property listed count,total property views count,status,joined,action(view,verify agent for verify badge,banned))

Sub Folder 7: Settings

Password Changes API
Terms and Conditions Get API + Post/Patch API (Rich Text)
Privacy and Policy Get API + Post/Patch API (Rich Text)
List all support message from user and agent +Reply to support message API

Add Property Type API + Edit + delete