export type Slide = {
  emoji: string;
  title: string;
  body: string;
  points?: string[];
};

export type TrainingModule = {
  id: string;
  title: string;
  audience: string;
  blurb: string;
  accent: string;
  slides: Slide[];
};

export const MODULES: TrainingModule[] = [
  {
    id: "organizer",
    title: "Organizer Training",
    audience: "New posters & organizers",
    blurb: "Learn to post free food on Second Course from both the mobile app and the web app.",
    accent: "bg-scGreen/25",
    slides: [
      {
        emoji: "👋",
        title: "Welcome, organizer!",
        body: "Second Course connects surplus food on campus with students who need it. As an organizer, you post available food and students claim it. This short course covers posting on both mobile and web.",
      },
      {
        emoji: "✅",
        title: "What makes a good post",
        body: "Great posts get claimed fast. Always include:",
        points: [
          "A clear title (e.g. 'Catered sandwiches & salads')",
          "An accurate pickup window — be realistic about timing",
          "A specific location, including building and room",
          "All known allergens (gluten, dairy, nuts, etc.)",
          "An honest serving count",
        ],
      },
      {
        emoji: "📱",
        title: "Posting on mobile",
        body: "In the app, tap the Posts tab, then '+ Post free food.' Snap a photo, fill in the title, location, pickup window, servings, and allergens, then publish. Students nearby get a notification instantly.",
      },
      {
        emoji: "💻",
        title: "Posting on the web app",
        body: "Prefer a laptop? Open the web app, choose Posts in the sidebar, and use the same form. The web app is ideal for catering staff and front-desk teams posting from a shared computer.",
      },
      {
        emoji: "💬",
        title: "Answer questions with live chat",
        body: "Each post has a live chat. Students may ask about ingredients, exact directions, or how much is left. Reply quickly — responsive posters get higher claim rates and less wasted food.",
      },
      {
        emoji: "🔒",
        title: "Safety & food handling",
        body: "Only post food that has been handled safely:",
        points: [
          "Keep hot food hot and cold food cold until pickup",
          "Don't post food left out longer than ~2 hours",
          "Label allergens honestly — when unsure, say so in the description",
          "Close the post once the food is gone or no longer safe",
        ],
      },
      {
        emoji: "🎉",
        title: "You're ready to post!",
        body: "That's it — you now know how to post safely on mobile and web and how to use live chat. Enter your name on the next screen to get your completion certificate.",
      },
    ],
  },
  {
    id: "dashboard",
    title: "Dashboard Training",
    audience: "University staff & admins",
    blurb: "Learn to read the university dashboard — metrics, demand maps, staff activity, and exports.",
    accent: "bg-scOrange/25",
    slides: [
      {
        emoji: "📊",
        title: "Welcome to the dashboard",
        body: "The university dashboard gives campus partners a real-time view of food recovery on their campus. This course walks through each section so you can pull insights and reports confidently.",
      },
      {
        emoji: "🏠",
        title: "Overview tab",
        body: "Start here for the big picture: total posts, total claims, claim rate, and average time to first claim, plus trend charts. Use the date-range selector to switch between week, month, and academic year.",
      },
      {
        emoji: "🗺️",
        title: "Demand map",
        body: "The Demand tab shows when and where posts perform best as a heatmap. Use it to plan staffing and outreach — for example, lunch hours at high-traffic buildings consistently see the highest claim rates.",
      },
      {
        emoji: "🧑‍🍳",
        title: "Staff activity",
        body: "The Staff tab tracks who is posting and flags underutilization. If a unit hasn't posted recently, you'll see a warning — a cue to reach out or offer a refresher training.",
      },
      {
        emoji: "🌱",
        title: "Impact & grant metrics",
        body: "The Impact tab estimates pounds of food diverted, climate impact, and waste-hauling savings. These grant-ready numbers are great for sustainability reports and funding applications.",
      },
      {
        emoji: "📁",
        title: "Exporting data",
        body: "The Exports tab downloads raw data as Excel or CSV and bundles every chart as PNG or SVG. Use these for internal review, audits, and presentations.",
      },
      {
        emoji: "🎓",
        title: "You're dashboard-ready!",
        body: "You now know how to navigate every section of the university dashboard. Enter your name on the next screen to get your completion certificate.",
      },
    ],
  },
];
