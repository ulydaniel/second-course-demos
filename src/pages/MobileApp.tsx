import { AppExperience } from "../components/app/AppExperience";

export default function MobileApp() {
  return (
    <div className="px-4 py-8">
      <div className="mx-auto max-w-5xl">
        <header className="mb-6 max-w-2xl space-y-2">
          <h1 className="font-display text-3xl text-black md:text-4xl">Mobile App</h1>
          <p className="font-sans text-black/80">
            The Second Course student app, including two new tabs — <strong>Resources</strong> and{" "}
            <strong>Offers</strong> — plus <strong>live chat</strong> on individual posts. Tap a feed
            post to open it and try the chat.
          </p>
        </header>

        <div className="flex justify-center">
          {/* Phone frame */}
          <div className="relative w-[360px] max-w-full">
            <div
              className="relative h-[740px] rounded-[44px] border-[6px] border-black bg-white p-3"
              style={{ boxShadow: "10px 10px 0 rgba(0,0,0,0.3)" }}
            >
              {/* Notch */}
              <div className="absolute left-1/2 top-0 z-10 h-6 w-36 -translate-x-1/2 rounded-b-2xl border-x-2 border-b-2 border-black bg-black" />
              {/* Screen */}
              <div className="h-full overflow-hidden rounded-[32px] border-2 border-black bg-white">
                <AppExperience variant="mobile" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
