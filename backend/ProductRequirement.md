# LocalChef - Product Requirements

## Authentication & Onboarding

### Login
- All users login via **phone number** (OTP-based authentication)
- No email/password authentication

### First-Time User Flow
1. Enter phone number → Receive OTP → Verify
2. Collect user details:
   - Name
   - Address (with map/location picker)
   - Address Type (Home, Work, Other) — similar to Swiggy
3. Redirect to Role Selection

### Existing User Flow
1. Enter phone number → Receive OTP → Verify
2. Show **Role Selection** screen:
   - **"I'm a Foodie"** — Order delicious home-cooked meals
   - **"I'm a Kitchen Owner"** — Start your own kitchen, share your favorite recipes

### Post Role Selection
- **Foodie**: Browse communities, discover kitchens, order food
- **Kitchen Owner**: View/manage their own kitchen, or browse other community kitchens to order

---

## User Roles

| Role | Description |
|------|-------------|
| Foodie | Orders food from home kitchens |
| Kitchen Owner | Runs a kitchen, manages menu, handles orders |

---

## Core Features

### Home Screen
- User location display (editable)
- Stories (Add Yours / Your Story)
- Search bar
- Banner/promotional area
- **Communities Near By** section with distance

### Communities
- All Communities / My Communities tabs
- Popular Communities listing
- Each community shows:
  - Name, image
  - Number of kitchens
  - Distance & location

### Kitchens
- Search with filters
- Kitchen cards showing:
  - Cover image
  - Kitchen name
  - Rating & reviews
  - Owner name
  - Preparation time
  - Community affiliation

### Kitchen Detail
- About, Photos, Reviews tabs
- FSSAI License number
- Delivery Type (Home Delivery / Self Pickup / Both)
- Address details
- **Request Food Order** & **View Menu** buttons

### Orders
- Tabs: New, Custom Orders, Past
- Order statuses: Pending, Pickup Pending, etc.
- Order details: ID, time, type (normal/custom), amount
- Delivery type badge (Home Delivery / Self Pickup)
- **Update Status** action

---

## Navigation (Bottom Tab)
1. Home
2. Orders
3. Community
4. Menu

---

## Data Schema

### User
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| phone_number | String | Unique, required for login |
| name | String | User's display name |
| profile_image | String | URL to profile photo |
| role | Enum | FOODIE, KITCHEN_OWNER |
| is_phone_verified | Boolean | Phone number verified via OTP |
| is_active | Boolean | Account status |
| created_at | DateTime | Registration timestamp |
| updated_at | DateTime | Last update timestamp |

### Address
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user | FK(User) | Owner of address |
| label | Enum | HOME, WORK, OTHER |
| address_line | String | Street address |
| landmark | String | Nearby landmark (optional) |
| city | String | City name |
| state | String | State name |
| pincode | String | Postal code |
| latitude | Decimal | GPS latitude |
| longitude | Decimal | GPS longitude |
| is_default | Boolean | Default delivery address |

### OTP
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| phone_number | String | Target phone number |
| code | String | 6-digit OTP |
| expires_at | DateTime | Expiration time |
| is_used | Boolean | Whether OTP was consumed |
| created_at | DateTime | Generation timestamp |

### Community
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| name | String | Community name |
| image | String | Community logo/image URL |
| description | Text | About the community |
| address | String | Location description |
| latitude | Decimal | GPS latitude |
| longitude | Decimal | GPS longitude |
| is_active | Boolean | Visibility status |
| created_at | DateTime | Creation timestamp |

### Kitchen
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| owner | FK(User) | Kitchen owner |
| community | FK(Community) | Associated community |
| name | String | Kitchen name |
| description | Text | About the kitchen |
| cover_image | String | Banner image URL |
| fssai_license | String | FSSAI license number |
| delivery_type | Enum | HOME_DELIVERY, SELF_PICKUP, BOTH |
| preparation_time | Integer | Avg prep time in minutes |
| opening_time | Time | Daily opening time |
| closing_time | Time | Daily closing time |
| address | String | Kitchen address |
| latitude | Decimal | GPS latitude |
| longitude | Decimal | GPS longitude |
| is_online | Boolean | Currently accepting orders |
| is_active | Boolean | Kitchen visibility |
| created_at | DateTime | Creation timestamp |

### KitchenPhoto
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| kitchen | FK(Kitchen) | Associated kitchen |
| image | String | Photo URL |
| caption | String | Optional description |
| created_at | DateTime | Upload timestamp |

### MenuItem
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| kitchen | FK(Kitchen) | Associated kitchen |
| name | String | Dish name |
| description | Text | Dish description |
| price | Decimal | Price in INR |
| image | String | Dish image URL |
| category | String | Veg, Non-Veg, etc. |
| is_available | Boolean | Currently available |
| created_at | DateTime | Creation timestamp |

### Order
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| order_number | String | Display ID (e.g., #99597356) |
| user | FK(User) | Customer |
| kitchen | FK(Kitchen) | Source kitchen |
| delivery_address | FK(Address) | Delivery location |
| status | Enum | PENDING, CONFIRMED, PREPARING, READY, PICKED_UP, DELIVERED, CANCELLED |
| order_type | Enum | NORMAL, CUSTOM |
| delivery_type | Enum | HOME_DELIVERY, SELF_PICKUP |
| total_amount | Decimal | Total order value |
| notes | Text | Special instructions |
| created_at | DateTime | Order placement time |
| updated_at | DateTime | Last status update |

### OrderItem
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| order | FK(Order) | Parent order |
| menu_item | FK(MenuItem) | Ordered item |
| quantity | Integer | Number of items |
| unit_price | Decimal | Price at time of order |
| subtotal | Decimal | quantity × unit_price |

### Review
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user | FK(User) | Reviewer |
| kitchen | FK(Kitchen) | Reviewed kitchen |
| order | FK(Order) | Associated order |
| rating | Integer | 1-5 stars |
| comment | Text | Review text |
| created_at | DateTime | Review timestamp |

### Story
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user | FK(User) | Story creator |
| kitchen | FK(Kitchen) | Associated kitchen (optional) |
| media_url | String | Image/video URL |
| media_type | Enum | IMAGE, VIDEO |
| expires_at | DateTime | Auto-delete time (24h) |
| created_at | DateTime | Upload timestamp |

### UserCommunity (M2M)
| Field | Type | Description |
|-------|------|-------------|
| user | FK(User) | Member |
| community | FK(Community) | Community |
| joined_at | DateTime | Join timestamp |
