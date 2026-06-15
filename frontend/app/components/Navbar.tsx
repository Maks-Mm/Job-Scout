import Image from "next/image";
import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="border-b bg-white">

      <div className="max-w-7xl mx-auto px-4">

        <div className="flex justify-between h-16">

          <Link
            href="/"
            className="flex items-center gap-2"
          >

            <Image
              src="/ImageScoutLogo.png"
              alt="JobRadar logo"
              width={40}
              height={40}
              className="rounded-lg object-contain"
            />

            <span className="text-xl font-bold text-blue-600">
              JobRadar
            </span>

          </Link>


          <div className="flex items-center gap-4">

            <Link
              href="/"
              className="text-gray-700 hover:text-blue-600"
            >
              Dashboard
            </Link>

            <Link
              href="/jobs"
              className="text-gray-700 hover:text-blue-600"
            >
              Jobs
            </Link>

            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg">
              Get Alerts
            </button>

          </div>

        </div>

      </div>

    </nav>
  );
}