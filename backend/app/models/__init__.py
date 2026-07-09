"""SQLAlchemy models — future tables mapped from the metrics spreadsheet.

Planned tables (see resources/Second Course Data Metrics - Sheet1.csv):

student_users
    Collected: full_name, university_email, year_in_school, major, graduation_year,
    demographics (age, gender, race, first_gen, international), housing, meal_plan,
    account_created_at, total_claims, claim_frequency, avg_notification_to_claim_min,
    days_since_last_activity
    Dashboard: money_saved, lbs_prevented, claim_history, top_orgs, campus_impact

food_posters (orgs)
    Collected: org_name, org_type, contact_name, university_email, verification_photo,
    member_count, posting_frequency, total_posts, active_status, post_descriptions
    Dashboard: total_claims, lbs_diverted, unique_students_reached, campus_impact

posts
    Per-post: description, allergens, location, posted_at, views, claims,
    first_claim_min, lbs_diverted

claims
    student_id, post_id, claimed_at (feeds engagement and demand grids)

dashboard_users
    email, role (administrator | editor | viewer), university_id
    Source: university AllowList document per PRD section 2
"""
