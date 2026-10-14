# erpv1 demo script

Written at the Stage 5 opening (PD-6, 2026-10-14), so the build provides everything the demo needs: the
data on screen, the users and the order of the pages. Runs on the local app (`mxcli run --local`; `--hub` for a
shared preview URL, PD-2). About 12 minutes, four acts that follow blueprint journeys J-01…J-04.

## Fixtures the demo needs (seeded per fixture-seeding.md, never typed live)

| Fixture | Values on screen | Needed by |
|---|---|---|
| Company | "erpv1 Demo B.V.", EUR, Netherlands, PO approval on, threshold 5 000 | all acts |
| Taxes | "21% (sales)", "21% (purchase)", "9%" | 1, 2 |
| Payment terms | "Immediate", "30 days" | 1, 2 |
| Units of measure | Units, Dozens (Unit category); kg, g (Weight) | 1, 2 |
| Warehouse | "WH" with Stock / Input / Output locations, receipt and delivery operation types | 1, 2, 3 |
| Customers | Azure Interior, Wood Corner (company), Deco Addict | 1, 4 |
| Vendors | Gemini Furniture, Ready Mat | 2, 3 |
| Products | Office Chair (storable, 120.00 / cost 70.00, vendor price Gemini 65.00), Desk Combination (storable, 450.00), Cable Pack (consumable, 12.50), Installation (service, 80.00/h) | 1, 2, 3 |
| Stock | Office Chair 8 on hand, Desk Combination 2 on hand | 1, 3 |
| Reorder rule | Office Chair min 10 / max 30, vendor Gemini Furniture | 3 |
| Sequences | S/P/WH-IN/WH-OUT/INV/BILL/RINV with next numbers that do not start at 1 (S00042…) | all |

Users: password `Erpv1-Demo-2026!` for every demo user (build plan row 14).

## Act 1 — Quote to cash (J-01), ~4 min

| Beat | User | Page | What the audience must see happen |
|---|---|---|---|
| 1.1 | sales.user | Quotations & orders | The list in the ledger theme: number, customer, date, total, status pill |
| 1.2 | sales.user | SalesOrder_NewEdit | New quotation for Azure Interior: number S000nn assigned, payment term defaulted from the customer |
| 1.3 | sales.user | SalesOrder_NewEdit | Add Office Chair × 5: unit price 120.00 from the product, tax 21%, line subtotal and order totals update |
| 1.4 | sales.user | SalesOrder_NewEdit | Mark as sent → status "Quotation sent"; Confirm → "Sales order", delivery smart button appears |
| 1.5 | warehouse.user | Transfer_NewEdit (WH/OUT) | Delivery for 5 chairs, 8 on hand → Validate → done; on-hand drops to 3 |
| 1.6 | sales.user | SalesOrder_NewEdit | Delivered quantity 5, invoice status "To invoice" |
| 1.7 | billing | CreateInvoice_Popup → Invoice_NewEdit | Create invoice → draft INV, Post → number INV/2026/000nn, amount due = total |
| 1.8 | billing | RegisterPayment_Popup | Register 300.00 → "Partially paid"; register rest → "Paid" |

## Act 2 — Procure with approval (J-02), ~4 min

| Beat | User | Page | What the audience must see happen |
|---|---|---|---|
| 2.1 | purchaser | PurchaseOrder_NewEdit | RFQ to Gemini Furniture: Desk Combination × 12, vendor price filled, total above the 5 000 threshold |
| 2.2 | purchaser | PurchaseOrder_NewEdit | Confirm → status "To approve" (the approval workflow starts) |
| 2.3 | purchase.manager | PurchaseApproval_Task (task inbox) | Task shows the order; Reject with reason "Negotiate price" → RFQ back to draft, reason visible |
| 2.4 | purchaser → purchase.manager | — | Purchaser lowers quantity/price, confirms again; manager approves → "Purchase order", receipt created |
| 2.5 | warehouse.user | Transfer_NewEdit (WH/IN) | Validate receipt → received quantities on the PO, on-hand up |
| 2.6 | billing | Invoice_NewEdit (vendor bill) | Create bill from PO, post, register outgoing payment |

## Act 3 — Replenishment (J-03), ~2 min

| Beat | User | Page | What the audience must see happen |
|---|---|---|---|
| 3.1 | inventory.manager | Inventory_Dashboard / StockLevel_Overview | Office Chair at 3, below the reorder minimum 10 |
| 3.2 | inventory.manager | ReorderRule_Overview | Run the reorder rules now (button runs the scheduled-event microflow) |
| 3.3 | purchaser | PurchaseOrder_Overview | New RFQ to Gemini Furniture for 27 chairs (up to max 30), source = the rule |

## Act 4 — Credit note and reporting (J-04), ~2 min

| Beat | User | Page | What the audience must see happen |
|---|---|---|---|
| 4.1 | billing | Invoice_NewEdit → CreditNote_Popup | Credit note for the paid invoice of act 1, reason "Damaged chair", 1 unit |
| 4.2 | billing | Invoice_NewEdit (credit note) | Posted RINV/2026/000nn, linked to the original |
| 4.3 | invoicing.manager | InvoiceAnalysis_Report | Receivables by customer: Azure Interior shows invoice and credit note |

## Warts to show, not hide (rule 8)

- No PDFs, no email sending, no portal: declared out of scope (Stage 0).
- Single company and single warehouse; no lots, packages or multi-step routes.
