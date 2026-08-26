# FRS Requirement Checklist - Asset Management System

## CF-3.1: Asset Record Access
- [ ] CF-3.1.1: System provides assets list/table for opening individual records
- [ ] CF-3.1.2: Opening asset shows core details only; no usage/installation/transfer/maintenance history
- [ ] CF-3.1.3: No merged timeline; each event type viewed in separate menu area

## CF-3.2: Installations, Vehicle Transfers, Maintenance  
- [ ] CF-3.2.1: Each accessed via own top-level sidebar menu item
- [ ] CF-3.2.2: Each menu lists records across all assets, filterable by asset ID
- [ ] CF-3.2.3: Cross-referencing single asset history requires separate navigation

## CF-3.3: Vehicle Usage
- [ ] CF-3.3.1: Accessed via own top-level sidebar, separate from asset record
- [ ] CF-3.3.2: Usage records logged/listed independently of other data types

## CF-3.4: Expenses
- [ ] CF-3.4.1: Tracked through separate workflow, not on asset record
- [ ] CF-3.4.2: Does not reuse step-by-step wizard pattern consistently
- [ ] CF-3.4.3: Approval status exists but not surfaced on Finance/Manager dashboard
- [ ] CF-3.4.4: Finding pending approvals requires manual search/filter

## CF-3.5: Asset Creation Wizard
- [ ] CF-3.5.1: New assets created through 4-step wizard
- [ ] CF-3.5.2: Does not autosave; data can be lost if abandoned
- [ ] CF-3.5.3: Validation at final submission, not inline/per-field
- [ ] CF-3.5.4: Dynamic Configuration always presented

## CF-3.6: Sidebar Navigation
- [ ] CF-3.6.1: Single sidebar for all users with operational & admin items
- [ ] CF-3.6.2: No workspace switcher or role-scoped sidebar
- [ ] CF-3.6.3: Admin access controlled by permissions, not menu hiding

## CF-3.7: Notifications
- [ ] CF-3.7.1: Single chronological list
- [ ] CF-3.7.2: Not grouped by severity
- [ ] CF-3.7.3: Not classified/filterable by type
- [ ] CF-3.7.4: Notification click goes to menu area, not specific record

## CF-3.8: Finance/Manager Dashboard
- [ ] CF-3.8.1: Does not display pending approval queue
- [ ] CF-3.8.2: Approval/rejection in expenses workflow, not dashboard
- [ ] CF-3.8.3: No count/badge for pending approvals

## Current Non-Functional Characteristics (CNFR)
- [ ] CNFR-1: Complete asset history requires multiple navigations
- [ ] CNFR-2: No autosave in wizard = data loss risk
- [ ] CNFR-3: Unscoped sidebar = clutter for users
