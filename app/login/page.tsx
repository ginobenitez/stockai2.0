import Link from "next/link"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Dashboard from "./dashboard"
/*export const description =
  "A login form with email and password. There's an option to login with Google and a link to sign up if you don't have an account."
*/


// Default export for the page
export default function HomePage() {
    return (
      <div>
        <Dashboard />
      </div>
    );
  }