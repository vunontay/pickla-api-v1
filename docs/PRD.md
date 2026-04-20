# Product Requirements Document (PRD)
## Pickleball Player Connection Platform — Phase 1

**Version:** 1.0.0
**Last Updated:** April 18, 2026
**Status:** Draft
**Owner:** Product Team

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Goals & Success Metrics](#2-goals--success-metrics)
3. [Target Users](#3-target-users)
4. [Core Features](#4-core-features)
5. [User Stories](#5-user-stories)
6. [System Architecture](#6-system-architecture)
7. [Data Models](#7-data-models)
8. [API Endpoints](#8-api-endpoints)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [Assumptions & Constraints](#10-assumptions--constraints)
11. [Decision Log](#11-decision-log)
12. [Implementation Plan](#12-implementation-plan)
13. [Out of Scope (Phase 1)](#13-out-of-scope-phase-1)
14. [Risks & Mitigations](#14-risks--mitigations)

---

## 1. Project Overview

### 1.1 Problem Statement

The Pickleball community in Vietnam is growing rapidly, yet players — especially individuals or incomplete groups — have no reliable, dedicated platform to find partners or fill open spots in a match. Current workarounds rely on fragmented Facebook groups, Zalo chats, and word-of-mouth, which are slow, unstructured, and difficult to scale.

### 1.2 Solution

A **mobile-first Web App** that serves as a marketplace for Pickleball matchmaking in Vietnam. The platform enables:

- **Hosts** (players who have a court or an organized session) to post open match slots.
- **Joiners** (individual players or incomplete groups) to discover and join available matches.
- A **Reputation Score** system to build community trust and reduce no-shows without requiring financial deposits.

### 1.3 Product Model

The platform operates on a **Marketplace-led + Host-led hybrid model**:

- **Marketplace Feed:** A public board displaying all available matches, allowing joiners to browse and filter in real-time.
- **Host-led Sessions:** Registered users who have access to a court can independently create and manage their match sessions, leveraging organic community participation.

### 1.4 Platform

- **Web App (Responsive)** — optimized for mobile browsers.
- No native app required in Phase 1; this reduces development cost and accelerates time-to-market.

---

## 2. Goals & Success Metrics

### 2.1 Business Goals

| Goal | Description |
|------|-------------|
| Validate PMF | Confirm that the matchmaking feature solves a real, recurring need in the Vietnamese Pickleball community. |
| Grow User Base | Acquire an initial base of active players and hosts within the first 3 months post-launch. |
| Build Trust | Establish the Reputation Score as a viable commitment mechanism, reducing no-shows. |

### 2.2 Key Performance Indicators (KPIs)

| Metric | Target (Month 3) |
|--------|-----------------|
| Registered Users | 500+ |
| Matches Posted per Week | 50+ |
| Match Fill Rate (slots filled / slots posted) | ≥ 70% |
| No-show / Late Cancel Rate | ≤ 15% |
| User Retention (Week 4) | ≥ 30% |
| Average Session Rating | ≥ 4.0 / 5.0 |

---

## 3. Target Users

### 3.1 User Personas

#### Persona A — The Solo Player ("Newbie Nam")
- **Age:** 22–35
- **Profile:** Recently started playing Pickleball; has no fixed group yet.
- **Pain Point:** Cannot find reliable partners; joins random Facebook groups and often gets no response.
- **Goal:** Quickly find a nearby match that fits their skill level and schedule.

#### Persona B — The Court Owner / Organizer ("Host Hung")
- **Age:** 28–45
- **Profile:** Rents a court regularly or owns a court; organizes sessions but always has 1–2 open slots.
- **Goal:** Fill open slots fast and play with a full, level-appropriate group; avoid wasted court fees.

#### Persona C — The Casual Group ("Weekend Warriors")
- **Age:** 25–40
- **Profile:** A group of 2–3 friends who play on weekends but need 1 more player to make a complete game.
- **Goal:** Find a trustworthy, skill-matched player to join their session quickly.

### 3.2 User Roles

| Role | Description |
|------|-------------|
| **Guest** | Can browse the public match feed without an account. |
| **Registered User** | Can create a profile, post matches (as Host), and join matches (as Joiner). |
| **Admin** | Internal role; manages users, moderates reports, and monitors platform health. |

---

## 4. Core Features

### 4.1 Account & Profile Management

#### 4.1.1 Registration & Authentication

- **Sign-up methods:** Phone number (OTP via SMS) or Social login (Google, Facebook).
- **Required profile fields on first login:**
  - Full name (display name)
  - Phone number / Zalo link (for in-match contact)
  - Location (Province / City → District)
  - Skill self-rating (see 4.1.2)
  - Profile photo (optional)

#### 4.1.2 Skill Self-Rating System

Users rate themselves on a **1.0 – 5.0 scale** with descriptive guidance to reduce over/under-rating:

| Level | Score | Description |
|-------|-------|-------------|
| Beginner | 1.0 – 1.5 | Just started; learning basic rules and strokes. |
| Novice | 2.0 – 2.5 | Understands rules; can sustain short rallies. |
| Intermediate | 3.0 – 3.5 | Consistent groundstrokes; understands positioning and strategy basics. |
| Advanced | 4.0 – 4.5 | Strong all-around game; participates in local tournaments. |
| Semi-Pro | 5.0 | Competitive tournament player; near-professional level. |

#### 4.1.3 Reputation Score

- **Starting value:** 100 points for all new users.
- **Purpose:** Acts as a social trust indicator, replacing a financial deposit in Phase 1.
- **Visibility:** Displayed on each user's public profile and on match participant lists.
- **Score changes:**

| Event | Points Change |
|-------|--------------|
| Confirmed attendance (match completed) | +2 |
| Joined match, attended on time | +1 |
| Cancelled within the allowed window (> 2 hours before) | 0 |
| Late cancellation (≤ 2 hours before match) | -10 |
| No-show (reported and confirmed) | -20 |
| Received positive rating from match partner | +3 |
| Received negative report (confirmed by admin) | -15 |

- **Consequence thresholds:**

| Score Range | Status | Restrictions |
|-------------|--------|--------------|
| 80 – 100+ | Good Standing | Full access |
| 50 – 79 | Cautioned | Warning badge shown to other users |
| Below 50 | Restricted | Cannot join new matches; can view feed only |

---

### 4.2 Match Discovery & Matchmaking Flow

#### 4.2.1 Host Flow — Creating a Match

A registered user can post a match session with the following information:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Court / Venue name | Text | Yes | Name and address of the court |
| District / City | Dropdown | Yes | Used for location-based filtering |
| Date & Time | DateTime picker | Yes | Must be at least 2 hours in the future |
| Duration | Dropdown | Yes | Options: 1h / 1.5h / 2h |
| Skill level required | Range slider | Yes | e.g., 2.5 – 3.5 |
| Open slots | Number (1–8) | Yes | Number of players still needed |
| Estimated cost per person | Number (VND) | No | Optional; entered by host for transparency |
| Match format | Dropdown | Yes | Singles / Doubles / Mixed |
| Notes / Description | Text area | No | Any additional info for joiners |

**Match status lifecycle:**

```
OPEN → FULL → CONFIRMED → COMPLETED
                ↓
             CANCELLED
```

#### 4.2.2 Joiner Flow — Finding & Joining a Match

**Match Feed (Public Board):**
- Default view: list of all `OPEN` matches, sorted by soonest start time.
- Each match card displays: Venue, Date/Time, Skill Range, Open Slots, Cost/person, Host Reputation Score.

**Filters available:**
- District / City
- Date range
- Skill level (my level ± 0.5)
- Time of day (Morning / Afternoon / Evening)
- Match format (Singles / Doubles / Mixed)
- Cost range

**Join Flow:**
1. Joiner taps **"Join Match"** on a match card.
2. System checks: Joiner's skill level falls within match's required range AND Joiner's Reputation Score ≥ 50.
3. If eligible: Joiner is added to the participant list; open slots count decrements by 1.
4. If match reaches 0 open slots: status changes to `FULL`.
5. Both Host and Joiner receive a **confirmation notification** with each other's contact info (phone / Zalo).

#### 4.2.3 Post-Match Connection

After a joiner is accepted:
- Both parties receive an **in-app notification** and (if opted in) an **SMS/Zalo message** containing:
  - Counterpart's display name
  - Phone number / Zalo link
  - Match details summary
- Further coordination (directions, exact meeting point, cost split) happens **directly between users** outside the app.

---

### 4.3 Commitment & Trust Mechanisms

#### 4.3.1 Cancellation Policy

| Time Before Match | Penalty |
|-------------------|---------|
| More than 2 hours | No penalty; slot reopens automatically |
| 2 hours or less | -10 Reputation Score |
| No-show (not cancelled) | -20 Reputation Score (after report confirmation) |

#### 4.3.2 Reminder & Confirmation System

| Trigger | Action |
|---------|--------|
| T-24 hours | Push notification / SMS reminder sent to all participants |
| T-4 hours | In-app prompt: **"Confirm your attendance"** button shown |
| T-2 hours | Final reminder; cancellation window closes |
| T-0 (match time) | System marks match as `IN PROGRESS` |
| T+2 hours | System prompts all participants to rate each other |

**Confirm Attendance:**
- Each participant must tap **"I'm Attending"** in the app before the 2-hour cutoff.
- Failure to confirm after T-4 hours sends an escalated reminder.
- Unconfirmed participants are flagged (no automatic removal in Phase 1; Host can manually remove).

#### 4.3.3 Reporting System

- Any participant can **report** another after a match for:
  - No-show
  - Late cancellation without valid reason
  - Inappropriate behavior
- Reports are queued for **admin review**.
- Upon admin confirmation, score deduction is applied.
- False/malicious reports are trackable; serial reporters may be flagged.

---

### 4.4 Notifications

| Notification | Channel | Trigger |
|-------------|---------|---------|
| New joiner applied to your match | In-app + SMS | When a joiner taps "Join Match" |
| Your join request confirmed | In-app + SMS | When slot is confirmed |
| Match reminder (24h) | In-app + SMS | 24 hours before match |
| Confirm attendance prompt (4h) | In-app | 4 hours before match |
| Match cancelled by Host | In-app + SMS | When host cancels |
| Match full | In-app | When all slots are filled |
| Reputation score changed | In-app | After report resolution or rating |

---

## 5. User Stories

### 5.1 Authentication

- `US-001` As a new user, I want to sign up with my phone number so I can create an account quickly.
- `US-002` As a returning user, I want to log in with Google so I don't have to remember a password.
- `US-003` As a user, I want to set my skill level during onboarding with clear descriptions so I self-rate accurately.

### 5.2 Match Hosting

- `US-004` As a Host, I want to create a match with venue, time, skill range, and open slots so others can find and join my session.
- `US-005` As a Host, I want to see a list of all players who have joined my match so I can coordinate with them.
- `US-006` As a Host, I want to cancel a match and notify all joiners automatically so nobody shows up unnecessarily.
- `US-007` As a Host, I want to close my match early (mark as Full) even if slots remain so I can stop receiving join requests.

### 5.3 Match Joining

- `US-008` As a Joiner, I want to browse available matches filtered by my district and skill level so I find relevant sessions quickly.
- `US-009` As a Joiner, I want to tap "Join Match" and immediately receive the host's contact info so I can coordinate directly.
- `US-010` As a Joiner, I want to cancel my spot with at least 2 hours notice so I don't lose Reputation Score.

### 5.4 Trust & Commitment

- `US-011` As a user, I want to see another player's Reputation Score on their profile so I can gauge their reliability.
- `US-012` As a Host, I want to receive a reminder 4 hours before the match so I can confirm all participants are attending.
- `US-013` As a user, I want to report a no-show so that unreliable players are penalized and the community stays trustworthy.
- `US-014` As a user, I want to rate my match partners after a session so that good players are rewarded.

### 5.5 Admin

- `US-015` As an Admin, I want to view all reported users and pending reports so I can review and act on violations.
- `US-016` As an Admin, I want to manually adjust a user's Reputation Score with a reason so I can handle edge cases fairly.
- `US-017` As an Admin, I want to deactivate or ban a user account so I can remove bad actors from the platform.

---

## 6. System Architecture

### 6.1 Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend (User) | **Next.js 16** (App Router) | SSR/SSG for SEO, responsive mobile-first UI, fast page loads |
| Frontend (Admin) | **React.js** (Vite + React Router) | SPA for internal admin dashboard; no SEO needed |
| Backend API | **FastAPI** (Python 3.12+) | High performance async API; excellent for rapid development and OpenAPI docs |
| Database | **PostgreSQL 16** | Relational data; reliable for transactional operations (reputation updates, match state) |
| Cache / Queue | **Redis** | Session management, notification queue, rate limiting |
| File Storage | **AWS S3** | Profile photos, static assets |
| SMS / OTP | **Twilio / ESMS Vietnam** | SMS notifications and OTP delivery |
| Containerization | **Docker + Docker Compose** | Consistent environments across dev/staging/prod |
| Cloud Infrastructure | **AWS** | EC2 (compute), RDS (PostgreSQL), ElastiCache (Redis), S3 (storage), CloudFront (CDN) |
| CI/CD | **GitHub Actions** | Automated testing and deployment pipeline |

### 6.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS Cloud                            │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐                      │
│  │  CloudFront   │    │   Route 53   │                      │
│  │     (CDN)     │    │    (DNS)     │                      │
│  └──────┬───────┘    └──────────────┘                      │
│         │                                                   │
│  ┌──────▼───────────────────────────────┐                  │
│  │          Application Load Balancer    │                  │
│  └──────┬──────────────────┬────────────┘                  │
│         │                  │                               │
│  ┌──────▼──────┐    ┌──────▼──────┐                       │
│  │  Next.js    │    │  React Admin │                       │
│  │  (EC2/ECS)  │    │  (EC2/ECS)  │                       │
│  └──────┬──────┘    └──────┬──────┘                       │
│         │                  │                               │
│  ┌──────▼──────────────────▼──────────┐                   │
│  │         FastAPI (EC2/ECS)           │                   │
│  │         REST API + WebSocket        │                   │
│  └──────┬──────────────────┬──────────┘                   │
│         │                  │                               │
│  ┌──────▼──────┐    ┌──────▼──────┐    ┌──────────────┐  │
│  │  PostgreSQL  │    │    Redis    │    │   AWS S3      │  │
│  │   (RDS)      │    │(ElastiCache)│    │  (Storage)    │  │
│  └─────────────┘    └─────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 7. Data Models

### 7.1 Entity Relationship Overview

```
User (1) ──────< Match (many)          [User as Host]
User (1) ──────< MatchParticipant (many) [User as Joiner]
Match (1) ─────< MatchParticipant (many)
User (1) ──────< Report (many)          [Reporter]
User (1) ──────< Report (many)          [Reported]
User (1) ──────< Rating (many)          [Rater]
User (1) ──────< Rating (many)          [Rated]
```

### 7.2 Table Definitions

#### `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK | Unique user identifier |
| `full_name` | VARCHAR(100) | NOT NULL | Display name |
| `phone_number` | VARCHAR(15) | UNIQUE, NOT NULL | Primary contact |
| `zalo_link` | VARCHAR(255) | NULLABLE | Optional Zalo profile URL |
| `email` | VARCHAR(255) | UNIQUE, NULLABLE | For social login |
| `avatar_url` | TEXT | NULLABLE | S3 URL for profile photo |
| `province` | VARCHAR(100) | NOT NULL | Province/City |
| `district` | VARCHAR(100) | NOT NULL | District |
| `skill_level` | DECIMAL(2,1) | NOT NULL, CHECK (1.0–5.0) | Self-rated skill level |
| `reputation_score` | INTEGER | NOT NULL, DEFAULT 100 | Trust score |
| `status` | ENUM | NOT NULL, DEFAULT 'active' | active / cautioned / restricted / banned |
| `auth_provider` | ENUM | NOT NULL | phone / google / facebook |
| `auth_provider_id` | VARCHAR(255) | NULLABLE | Social login UID |
| `is_admin` | BOOLEAN | NOT NULL, DEFAULT false | Admin flag |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Registration timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

#### `matches`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK | Unique match identifier |
| `host_id` | UUID | FK → users.id | Match creator |
| `venue_name` | VARCHAR(255) | NOT NULL | Court / venue name |
| `venue_address` | TEXT | NOT NULL | Full address |
| `province` | VARCHAR(100) | NOT NULL | Province/City |
| `district` | VARCHAR(100) | NOT NULL | District |
| `start_time` | TIMESTAMP | NOT NULL | Match start date & time |
| `duration_minutes` | INTEGER | NOT NULL | 60 / 90 / 120 |
| `skill_min` | DECIMAL(2,1) | NOT NULL | Minimum skill level required |
| `skill_max` | DECIMAL(2,1) | NOT NULL | Maximum skill level required |
| `total_slots` | INTEGER | NOT NULL | Total player slots for the match |
| `open_slots` | INTEGER | NOT NULL | Remaining open slots |
| `format` | ENUM | NOT NULL | singles / doubles / mixed |
| `cost_per_person` | INTEGER | NULLABLE | Estimated cost in VND |
| `notes` | TEXT | NULLABLE | Additional info from host |
| `status` | ENUM | NOT NULL, DEFAULT 'open' | open / full / confirmed / in_progress / completed / cancelled |
| `cancelled_reason` | TEXT | NULLABLE | Reason if cancelled |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

#### `match_participants`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK | Unique record identifier |
| `match_id` | UUID | FK → matches.id | Related match |
| `user_id` | UUID | FK → users.id | Participating user |
| `status` | ENUM | NOT NULL, DEFAULT 'joined' | joined / confirmed / cancelled / no_show |
| `confirmed_at` | TIMESTAMP | NULLABLE | When user confirmed attendance |
| `cancelled_at` | TIMESTAMP | NULLABLE | When user cancelled |
| `joined_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | When user joined |

#### `reputation_logs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK | Log entry ID |
| `user_id` | UUID | FK → users.id | Affected user |
| `change` | INTEGER | NOT NULL | Points added or deducted |
| `reason` | VARCHAR(255) | NOT NULL | Human-readable reason |
| `reference_type` | ENUM | NULLABLE | match / report / rating |
| `reference_id` | UUID | NULLABLE | ID of related entity |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Timestamp |

#### `reports`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK | Report ID |
| `reporter_id` | UUID | FK → users.id | User who filed the report |
| `reported_id` | UUID | FK → users.id | User being reported |
| `match_id` | UUID | FK → matches.id | Match context |
| `reason` | ENUM | NOT NULL | no_show / late_cancel / inappropriate |
| `description` | TEXT | NULLABLE | Optional additional details |
| `status` | ENUM | NOT NULL, DEFAULT 'pending' | pending / confirmed / rejected |
| `reviewed_by` | UUID | FK → users.id, NULLABLE | Admin who reviewed |
| `reviewed_at` | TIMESTAMP | NULLABLE | Review timestamp |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Report filed timestamp |

#### `ratings`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK | Rating ID |
| `match_id` | UUID | FK → matches.id | Match context |
| `rater_id` | UUID | FK → users.id | User giving the rating |
| `rated_id` | UUID | FK → users.id | User being rated |
| `score` | INTEGER | NOT NULL, CHECK (1–5) | 1–5 star rating |
| `comment` | TEXT | NULLABLE | Optional written feedback |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Rating timestamp |

---

## 8. API Endpoints

### 8.1 Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register/phone` | Register with phone number + OTP |
| `POST` | `/api/v1/auth/verify-otp` | Verify OTP and complete registration |
| `POST` | `/api/v1/auth/login/social` | Login with Google / Facebook token |
| `POST` | `/api/v1/auth/refresh` | Refresh access token |
| `POST` | `/api/v1/auth/logout` | Invalidate tokens |

### 8.2 Users & Profiles

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/users/me` | Get current user profile |
| `PUT` | `/api/v1/users/me` | Update current user profile |
| `GET` | `/api/v1/users/{user_id}` | Get public profile of any user |
| `GET` | `/api/v1/users/me/reputation-log` | Get current user's reputation history |

### 8.3 Matches

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/matches` | List all open matches (with filters) |
| `POST` | `/api/v1/matches` | Create a new match (Host only) |
| `GET` | `/api/v1/matches/{match_id}` | Get match details |
| `PUT` | `/api/v1/matches/{match_id}` | Update match (Host only, if OPEN) |
| `DELETE` | `/api/v1/matches/{match_id}` | Cancel a match (Host only) |
| `GET` | `/api/v1/matches/{match_id}/participants` | Get participant list |
| `POST` | `/api/v1/matches/{match_id}/join` | Join a match (Joiner) |
| `DELETE` | `/api/v1/matches/{match_id}/leave` | Leave / cancel a match (Joiner) |
| `POST` | `/api/v1/matches/{match_id}/confirm` | Confirm attendance |
| `GET` | `/api/v1/users/me/matches` | Get current user's matches (hosted + joined) |

### 8.4 Reports & Ratings

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/reports` | Submit a report against a user |
| `GET` | `/api/v1/reports` | List all reports (Admin only) |
| `PUT` | `/api/v1/reports/{report_id}` | Review/resolve a report (Admin only) |
| `POST` | `/api/v1/ratings` | Submit a rating for a match participant |

### 8.5 Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/admin/users` | List all users with filters |
| `PUT` | `/api/v1/admin/users/{user_id}/status` | Update user status (ban, restrict, etc.) |
| `PUT` | `/api/v1/admin/users/{user_id}/reputation` | Manually adjust reputation score |
| `GET` | `/api/v1/admin/matches` | List all matches |
| `GET` | `/api/v1/admin/stats` | Platform health statistics |

### 8.6 Filter Query Parameters (GET /api/v1/matches)

| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `district` | string | `"Hai Chau"` | Filter by district |
| `province` | string | `"Da Nang"` | Filter by province |
| `skill_min` | float | `2.5` | Minimum skill level |
| `skill_max` | float | `3.5` | Maximum skill level |
| `date_from` | date | `"2026-04-20"` | Start of date range |
| `date_to` | date | `"2026-04-25"` | End of date range |
| `time_of_day` | string | `"morning"` | morning / afternoon / evening |
| `format` | string | `"doubles"` | singles / doubles / mixed |
| `cost_max` | integer | `100000` | Max cost per person (VND) |
| `page` | integer | `1` | Pagination page number |
| `limit` | integer | `20` | Items per page (max 50) |

---

## 9. Non-Functional Requirements

### 9.1 Performance

| Requirement | Target |
|-------------|--------|
| API Response Time (p95) | < 300ms |
| Match Feed Load Time | < 1.5s on 4G mobile |
| Concurrent Users (Phase 1) | Support up to 500 |
| Database Query Optimization | Indexes on `district`, `start_time`, `status`, `skill_min/max` |

### 9.2 Security

- All API endpoints use **JWT Bearer Token** authentication (access token + refresh token).
- Passwords (if used in future) must be hashed with **bcrypt**.
- Sensitive user data (phone number, Zalo link) is only revealed to matched participants, not in public listings.
- Phone numbers are partially masked in public match cards (e.g., `090***789`).
- Rate limiting applied on OTP endpoints (max 3 requests per 10 minutes per phone number).
- HTTPS enforced across all services.

### 9.3 Scalability

- Stateless API services allow **horizontal scaling** via AWS Auto Scaling Groups.
- PostgreSQL connection pooling via **PgBouncer**.
- Redis used for caching frequently read data (match feed, user profiles).
- Background notification jobs processed via **Redis Queue (RQ)** worker service.

### 9.4 Availability

- Target SLA: **99.5% uptime** (Phase 1).
- Database backups: automated daily snapshots via AWS RDS.
- Application logs shipped to **AWS CloudWatch**.

### 9.5 Accessibility & UX

- Mobile-first responsive design; tested on iOS Safari and Android Chrome.
- Minimum tap target size: 44×44px.
- Support Vietnamese language (default); English as secondary.
- Loading states and error messages in all interactive components.

---

## 10. Assumptions & Constraints

| # | Type | Statement |
|---|------|-----------|
| A1 | Assumption | Users are willing to share their phone number / Zalo contact with matched players for direct coordination. |
| A2 | Assumption | The Reputation Score system provides sufficient social pressure to reduce no-shows and late cancellations in Phase 1, without requiring a financial deposit. |
| A3 | Assumption | Financial transactions (court fee splitting) happen directly between players. The platform does not process or guarantee payments. |
| A4 | Assumption | The initial user base will be concentrated in major Vietnamese cities (Ho Chi Minh City, Hanoi, Da Nang). |
| A5 | Assumption | Hosts take responsibility for the accuracy of court/venue information they post. |
| C1 | Constraint | No in-app payment processing in Phase 1. |
| C2 | Constraint | No native mobile app (iOS/Android) in Phase 1; Web App only. |
| C3 | Constraint | Admin moderation of reports is manual in Phase 1 (no automated ML-based moderation). |
| C4 | Constraint | SMS notification costs must be kept within budget; batching and throttling applied. |

---

## 11. Decision Log

| # | Issue / Question | Decision | Rationale | Date |
|---|-----------------|----------|-----------|------|
| D1 | What should be the core MVP feature? | **Matchmaking (Find & Fill a Match)** | This is the most critical unmet need; all other features support it. | — |
| D2 | How to handle commitment without payments? | **Reputation Score system** | Reduces onboarding friction while providing a social deterrent against no-shows. Payments can be added in Phase 2. | — |
| D3 | What operational model to use? | **Host-led + Marketplace Feed hybrid** | Leverages the existing community's self-organizing behavior, reducing the need for platform-managed sessions. | — |
| D4 | What platform to build for? | **Responsive Web App (Next.js)** | Fastest and most cost-effective path to reach users. Native apps can be added in Phase 2 once PMF is validated. | — |
| D5 | How to structure the match discovery UI? | **Marketplace Feed (card-based list)** | Users can immediately see available options without searching; reduces friction for new users. | — |
| D6 | What backend framework to use? | **FastAPI (Python)** | Async performance, automatic OpenAPI docs, fast iteration speed, and strong ecosystem for future ML features (smart matchmaking). | — |
| D7 | What is the cancellation deadline? | **2 hours before match start** | Balances user flexibility with sufficient time for the host to find a replacement joiner. | — |

---

## 12. Implementation Plan

### Phase 1 — MVP (Target: 8 weeks)

#### Milestone 1: Foundation (Weeks 1–2)
**Goal:** Project scaffolding, auth, and basic profile.

- [ ] Set up monorepo structure with Docker Compose
- [ ] Configure AWS infrastructure (EC2, RDS, S3, ElastiCache)
- [ ] Implement user registration (phone + OTP) and social login
- [ ] Build user profile creation and edit flows
- [ ] Implement skill self-rating onboarding screen
- [ ] Set up CI/CD pipeline (GitHub Actions)

#### Milestone 2: Core Matchmaking (Weeks 3–4)
**Goal:** Host can post matches; Joiner can find and join matches.

- [ ] Build match creation form (Host flow)
- [ ] Build match feed with card UI (Joiner view)
- [ ] Implement search filters (district, skill, time, format)
- [ ] Build "Join Match" flow with eligibility check
- [ ] Implement match status transitions (open → full → confirmed)
- [ ] Expose contact info to matched participants
- [ ] Build "My Matches" dashboard for both Host and Joiner

#### Milestone 3: Commitment & Trust (Weeks 5–6)
**Goal:** Reputation system and reminder flow operational.

- [ ] Implement Reputation Score logic (earn/deduct events)
- [ ] Build reputation log view on user profile
- [ ] Implement T-24h and T-4h reminder notifications (SMS + in-app)
- [ ] Build "Confirm Attendance" flow
- [ ] Implement cancellation flow with penalty logic
- [ ] Build post-match rating prompt and submission

#### Milestone 4: Reporting & Admin (Weeks 7–8)
**Goal:** Moderation tools and platform stabilization.

- [ ] Build report submission flow (no-show, late cancel, behaviour)
- [ ] Build React Admin dashboard (user list, match list, report queue)
- [ ] Implement admin report review and reputation adjustment
- [ ] Build admin platform stats page
- [ ] Mobile UI audit and optimization
- [ ] Performance testing and load testing
- [ ] Security review and penetration testing basics

---

## 13. Out of Scope (Phase 1)

The following features are explicitly deferred to Phase 2 or later:

| Feature | Notes |
|---------|-------|
| In-app payment / escrow | Court fee splitting handled offline; no payment gateway in Phase 1. |
| Native iOS / Android app | Web App only in Phase 1. |
| Smart/AI matchmaking | Basic filter-based matching only. ML-powered suggestions deferred. |
| Tournament / league management | Out of scope; separate product consideration. |
| Court booking / reservation | Platform does not integrate with court booking systems in Phase 1. |
| In-app chat / messaging | Users communicate via phone / Zalo after matching. |
| Verified skill rating | Only self-rating in Phase 1; third-party skill verification (e.g., by certified coaches) is future work. |
| Multiple languages | Vietnamese only in Phase 1. |
| Push notifications (native) | Web push notifications are stretch goal; SMS is primary channel. |

---

## 14. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Low initial supply of Hosts → sparse match feed | High | High | Seed the platform with organically recruited hosts from existing Facebook/Zalo groups before launch. |
| Reputation Score insufficient to deter no-shows | Medium | High | Monitor no-show rate closely in Month 1; be ready to introduce financial deposit in Phase 2 if needed. |
| Users unwilling to share phone numbers | Medium | Medium | Make contact sharing opt-in with clear privacy explanation; mask phone numbers partially in public view. |
| SMS delivery failures / cost overruns | Low | Medium | Use reputable Vietnam-local SMS gateway (e.g., ESMS, VIVAS); implement fallback in-app notifications. |
| Host posts incorrect court info → user friction | Medium | Medium | Add a "Report incorrect info" button on match cards; encourage photo upload for venues. |
| Fraudulent or spam match postings | Low | Medium | Require phone verification for all users; implement rate limiting on match creation (max 3 active matches per user). |
| Technical scaling bottlenecks on launch day | Low | High | Load test before launch; set up AWS Auto Scaling; use Redis for match feed caching. |

---

*This document is a living specification. All sections should be reviewed and updated at the start of each development milestone. Breaking changes to the data model or API contract require a version bump and team sign-off.*

---

**Document Owner:** Product Team
**Last Reviewed:** April 18, 2026
**Next Review:** Before Milestone 2 kickoff