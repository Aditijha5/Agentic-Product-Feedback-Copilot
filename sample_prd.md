# Example PRD output (illustrative)

_This shows the format the PRD agent produces. The content below is an illustrative example written from synthetic reviews, not a result from real user data._

## Theme: Checkout and payment failures

### Problem Statement
Users report that payments fail or orders get stuck at checkout, and some say they were still charged. This blocks the core purchase flow and damages trust.

### Evidence
- Reviews in this theme skew to 1-2 stars and high severity.
- Representative (synthetic) quotes: "Payment fails at checkout and I still get charged", "Order status is stuck on processing forever".

### Target Users
Shoppers completing a first or repeat purchase, especially on mobile.

### User Stories
1. As a shopper, I want a clear failure message with a retry option, so that I can complete my purchase without starting over.
2. As a shopper, I want to see whether I was charged when a payment fails, so that I don't pay twice.
3. As a support agent, I want failed-payment events logged with a reason, so that I can resolve disputes quickly.

### Proposed Solution (high level)
Add explicit payment-state handling with automatic reconciliation of charged-but-failed orders and a guided retry flow.

### Acceptance Criteria
- A failed payment always shows a specific reason and a retry action.
- A charged-but-failed order is auto-reconciled or flagged within a defined time window.
- Order status never stays in "processing" beyond a defined limit without escalation.
- Payment failures are logged with reason codes.

### Success Metrics
- Checkout completion rate
- Payment failure rate and charged-but-failed incidents
- Support tickets tagged "payment"

### Risks and Open Questions
- Dependence on the payment provider's webhooks.
- Which failures are provider-side vs app-side?
