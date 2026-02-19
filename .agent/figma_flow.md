# User FLOW:

* Splash Screen

* Login: (email,password) + google login + apple login + refresh token(api)

* Signup (Registration) : Full Name , email , phone, password

* Forget Pass: send otp to email, verify otp, update password(new password, confirm password)

* Profile API : Get , Patch 

* Home Screen : All public property list
                - Property filtering (All/Houses/Apartments/Villas)
                - Property listing
                - Property details (offer type :featured, under offer,New (if added within last 7days),title,rating,address,beds, bath,size,prize, location (lat,long))
                - user can add to their favourite list among them and - remove from favourite list
                - search by area, locatiom, postcode , name, price, bed rooms etc

* Property details:
                - available status
                - all images
                - title, address, price, bed rooms, bath rooms, size, location (lat,long),parking slot count
                - description
                - property video
                - property 360 tour
                - location lat , lon
                - similar property list
                - schedule to book for physical checking  ( date, time, message to agent(optional))
                - based on property price , user can make an offer to negotiate
                - Make offer (full name, email,phone,offer ammount ,message(optional))
                - view agent information of that property(Brand/agent name,website,rating,phone no, email,give rating )

* Search :
        - all property list
        - can be search my (price range),property type(house, apartment, villas), Amenities(parking,pet friendly,garden,poor), bedroom (any, 1,2,3,4,5+), text search(name/location/postcode)

* QR Search :
        - scan QR code on physical board
        - redirect to property details page

* Favorite:
        - all favourite list of user (can be filter by property type - house,apartment,villas)
        - remove from favourite list

* Account settings:
        - profile (name,email,phone,profile picture,member since,favourtie property list count, user's property list count, location)
        - change password
        - notifications (push, email)
        - logout
        - edit profile (patch)
        - saved/fv properties api
        - get api terms and conditions
        - get api privacy and policy
        - post api for admin support message
        - my property list
        - delete user account (post request to solid confirmation)
        - push notifcation toggle
        - email update toggle
        - two factor authentication (email based for now)

* Chat bot:
        - Chat with AI only based FAQ (ai developer will create a fastapi chatbot service for me from where i will share all faq and ai will ans based on faq)
        

=========================================================================

* Agent Flow:
- login (email, pass)
- signup (full name, email, number,password)
- Forget Pass: send otp to email, verify otp, update password(new password, confirm password)
- home screen : (total listing count of agent,total views count of agent's properties,total leads/got offer count,total qr scaneed on his properties count)
- all recent activities of agent (format: title,activity info(example: new offer recieed,qr code scannned to this property,lead inquiry etc ),time (1 hour age))



* Home Screen : All public property list
                - Property filtering (All/Houses/Apartments/Villas)
                - Property listing
                - Property details (offer type :featured, under offer,New (if added within last 7days),title,rating,address,beds, bath,size,prize, location (lat,long))
                - user can add to their favourite list among them and - remove from favourite list
                - search by area, locatiom, postcode , name, price, bed rooms etc

* Add properties:
- properties images
- title
- type (House, APartment, vilaas)
- price
- address
- key features (bedroom count,bathroom count,size,parking slot count,pool,garage,garden,fireplace,smart home,gym)
- upload agent video
- location link (google map link , lon/lat)
- add preview to see listing
- save property
- save and qr generate to scan to see this property
- download qr code


* offer / leads
- all offer and lead listing(filter by :all,accepted,pending,rejected)
- listing (user name,property title,offer amout,date, time,message,email, phone,offer status(pending /accepted/ rejected))
- accept 
- reject
- add to leads
- counter offer (whole counter ooffer history, orginal details, user offer, agent counter offer all history)


* agency profile:
- image
- agent/brand name
- verified by admin
- member sicne
- total property listing count , total offer recieved count
- edit company and profile (logo,name,brand color,website, agent photo,agent name,email,phone,)
- passowd update
- all leads listing (call/email)
- delete account
- notification(push/email)



=====================================================

*** Admin Flow
- email and password login
- dashboard (total aagent count, total agent active count, total agent pending verification count ,total property listed count on full site,total users, total property views count on whole platform)
- property count (villa count, apartment count ,house count)
- Recent activities:
    - title agent added new properties , 15 mins ago
    - mike chan closed a deal - $1.2m , 1 hour ago
    - new agent registration - emman devis

- pending propery approve list post

- all property list ( filter by status (all,approved, rejected), filer by types (house, apartment, vilals,)serch using text based charact )
- pending property post (approved, reject, view details)
- user management (full name,email,status,role,join data,last active,action(view/banned)) [pagination]
- agent managment (agent name,agency/company name,property listed count,total property views count,status,joined,action(view,verify agent for verify badge,banned))
- 

* admin settings:
** general:
            - password update
            - terms and conditions ( rich text)
            - privacy and policy ( rich text)
            - property type setting add/remove (house,apartment,villa etc)
            - support and help message (reply any message come for support)
