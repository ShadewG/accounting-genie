# Firestore Database Schema

This document outlines the initial Firestore collections for the project. These structures are designed around the Fiken API integration requirements.

## Collections

### 1. `users`
Stores user information and authentication details.

| Field | Type | Description |
|-------|------|-------------|
| `email` | `string` | User's email address. |
| `displayName` | `string` | Optional user-friendly name. |
| `fikenAccessToken` | `string` | OAuth token for Fiken API access. |
| `fikenRefreshToken` | `string` | OAuth refresh token. |
| `createdAt` | `timestamp` | When the user was created. |
| `updatedAt` | `timestamp` | Last time the record was updated. |

### 2. `receipts`
Metadata about uploaded receipts and their processing status.

| Field | Type | Description |
|-------|------|-------------|
| `userId` | `reference` | Reference to the user who uploaded the receipt. |
| `filePath` | `string` | Location of the file in storage. |
| `vendor` | `string` | Vendor extracted from the receipt. |
| `date` | `timestamp` | Date of the receipt. |
| `totalAmount` | `number` | Total amount on the receipt. |
| `currency` | `string` | Currency code (e.g., `NOK`, `USD`). |
| `status` | `string` | Processing state: `pending_ocr`, `pending_review`, `posted_to_fiken`, etc. |
| `extractedData` | `map` | Raw OCR results or parsed fields. |
| `createdAt` | `timestamp` | When the receipt was uploaded. |
| `updatedAt` | `timestamp` | Last update time. |

### 3. `rules`
Custom categorization rules for mapping receipts to accounts or Fiken categories.

| Field | Type | Description |
|-------|------|-------------|
| `userId` | `reference` | Reference to the user who owns the rule. |
| `matchVendor` | `string` | Vendor name or pattern to match. |
| `account` | `integer` | Accounting account to assign. |
| `vatType` | `string` | VAT category (e.g., `HIGH`, `LOW`). |
| `description` | `string` | Optional explanation of the rule. |
| `createdAt` | `timestamp` | When the rule was created. |
| `updatedAt` | `timestamp` | When the rule was last modified. |

## Status Values for Receipts
- `pending_ocr`: Receipt image uploaded but waiting for OCR processing.
- `pending_review`: Data extracted; user needs to confirm before posting.
- `posted_to_fiken`: Receipt has been sent to Fiken as an expense or supplier invoice.

These collections provide a starting point for managing users, receipts, and categorization logic in Firestore. They align with the data required for interacting with the Fiken API.
