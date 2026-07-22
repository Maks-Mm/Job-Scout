//frontend/app/components/Navbar.tsx

import Image from "next/image";
import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="border-b bg-white">

      <div className="max-w-7xl mx-auto px-4">

        <div className="flex justify-between h-16">

          <div className="flex items-center gap-2">
            <img
              src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSUC6HSLegg6eairvNwiY42n1ik5VIcynMo9vs19eHzpw&s"
              alt="JobRadar Logo"
              className="h-10 w-17 rounded"
            />
          </div>


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