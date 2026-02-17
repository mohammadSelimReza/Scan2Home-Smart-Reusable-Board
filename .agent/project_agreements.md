# Project Specification: Scan2Home — “Smart Reusable Board”

## 1. Project Overview
Scan2Home is a QR code-driven real estate platform designed to bridge the gap between physical "For Sale" signs and digital property listings. By utilizing dynamic QR codes, the platform enables potential buyers to instantly access property data, while providing agents with a reusable, "zero-waste" hardware solution.

### Purpose
To modernize the property-buying process, reduce physical friction, and provide real-time lead generation for agents through seamless mobile interactions.

---

## 2. System Architecture & Tech Stack

### Frontend (Mobile & Web)
- **Framework:** Flutter (Cross-platform iOS/Android)
- **Language:** Dart
- **Design:** Figma (UI/UX)

### Backend (Server & API)
- **Framework:** Django / Django REST Framework (DRF)
- **Language:** Python
- **Real-time:** Socket.io / Django Channels (Notifications & Messaging)
- **AI Engine:** Python-based Chatbot (OpenAI API or Custom LLM)

### Database & Storage
- **Primary Database:** PostgreSQL
- **File Storage:** AWS S3 (Property images/documents)

### Infrastructure & DevOps
- **Hosting:** AWS (EC2), Digital Ocean, or GCP
- **CDN:** CloudFront
- **Payment Gateway:** Stripe API

---

## 3. Core Feature List

### Buyer Role
- **Instant Scan:** Scan QR code to redirect to property landing pages.
- **Property Discovery:** View high-res photos, descriptions, and amenities.
- **Offer Management:** Submit offers via a streamlined digital form.
- **Scheduling:** Book viewings based on live agent availability calendars.
- **Notifications:** Receive automated email/push confirmations for bookings.
- **Personal Dashboard:** View history of scanned properties and submitted offers.

### Seller/Agent Role
- **Dynamic QR Management:** Reassign a single physical board to a new listing once the previous property is sold.
- **Lead Generation:** Get instant notifications when a buyer scans a code or submits an offer.
- **Dashboard:** Manage property listings, upload photos, and track analytics (scan counts, engagement).
- **Availability Management:** Set time slots for property viewings.

### Admin Role
- **User Management:** Oversee buyer and agent accounts.
- **Content Moderation:** Manually manage/audit listings and offers.
- **Reporting:** Generate system-wide reports on scans, conversions, and sales.
- **Security:** Manage roles, permissions, and data privacy protocols.

### AI Role Features
- **AI Chatbot:** 24/7 assistant to answer buyer FAQs regarding property details or the buying process.
- **Summarizer:** Auto-generate summaries of property descriptions and offer terms for agents.

---

## 4. Logic & API Flow (Smart Reusable Board)

Based on the **"Smart Reusable Board" Concept Diagram**, the API logic follows this lifecycle:

1.  **The Trigger:** Buyer scans a unique QR Code on a physical board.
2.  **The Redirect (API Layer):** 
    - Request: `GET /api/v1/qr/{qr_id}`
    - Logic: Backend checks the current active mapping for `{qr_id}`.
    - Response: Redirects user to the specific Property Listing URL.
3.  **Lead Capture:** Agent receives an instant notification via WebSockets/Email.
4.  **The Reassignment:**
    - Property is marked as "Sold" or "Let".
    - Agent accesses Dashboard -> Clicks **"Reassign Board"**.
    - API Request: `PATCH /api/v1/boards/{qr_id}/reassign` (Payload: `new_property_id`).
5.  **Cycle Repeats:** The same physical QR code now points to a completely different property listing.

---

## 5. Development Roadmap & Budget

| Phase | Task | Technology | Timeline | Price (USD) |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1** | UI/UX Design (App & Admin) | Figma | 20 Days | $2,500 |
| **Phase 2** | Frontend Development (Web/App) | Flutter | 20 Days | $2,200 |
| **Phase 3** | AI Development & Integration | Python | 15 Days | $1,500 |
| **Phase 4** | API, Backend & Admin Dashboard | Django, PostgreSQL | 25 Days | $1,600 |
| **Phase 5** | Deployment & Publishing | AWS/Store Policy | Per Policy | $200 |
| **Total** | | | **70 Days** | **$8,000** |

---

## 6. Deliverables
- **Original APK/IPA:** Installation files for Android and iOS.
- **Source Code:** Full access to the GitHub/GitLab repository.
- **Design Assets:** Original Figma files.
- **Documentation:** API documentation and deployment guide.
- **Support:** 120 days of ongoing post-completion maintenance and support.

---

## 7. Compliance & Security
- **Data Privacy:** GDPR/CCPA compliance for user data.
- **Secure Payments:** All transactions handled via Stripe PCI-compliant servers.
- **Scalability:** Hosted on AWS/Digital Ocean to handle traffic spikes during peak real estate hours.