"use client";

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { NavigationMenu, NavigationMenuList, NavigationMenuItem, NavigationMenuLink } from "@/components/ui/navigation-menu";
import Image from "next/image";
import Link from "next/link";
import { FileText, Eye, Headphones, FileEdit, FolderOpen } from "lucide-react";

export default function Home() {
  const features = [
    {
      title: "Reading Tests",
      description: "Assess reading speed and comprehension with AI-powered analytics",
      icon: <FileText className="w-6 h-6" />,
      href: "/reading-test"
    },
    {
      title: "Contrast Test",
      description: "Find the most comfortable text and background color combinations",
      icon: <Eye className="w-6 h-6" />,
      href: "/contrast-test"
    },
    {
      title: "Dictation Test",
      description: "Practice writing through speech-to-text with instant feedback",
      icon: <Headphones className="w-6 h-6" />,
      href: "/dictation-test"
    },
    {
      title: "Notes Proofreading",
      description: "AI-powered correction for spelling and grammar",
      icon: <FileEdit className="w-6 h-6" />,
      href: "/proofreading"
    },
    {
      title: "Open Text File",
      description: "Import and analyze text files with dyslexia-friendly formatting",
      icon: <FolderOpen className="w-6 h-6" />,
      href: "/open-file"
    }
  ];

  return (
    <div className="min-h-screen p-8">
      <header className="mb-12">
        <NavigationMenu className="justify-between max-w-screen-xl mx-auto">
          <NavigationMenuList>
            <NavigationMenuItem>
              <h1 className="text-3xl font-bold">DyslexiAssist</h1>
            </NavigationMenuItem>
          </NavigationMenuList>
        </NavigationMenu>
      </header>

      <main className="max-w-screen-xl mx-auto">
        <section className="mb-12 text-center">
          <h2 className="text-4xl font-bold mb-4">AI-Powered Dyslexia Assistance</h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Enhance your reading and writing experience with our suite of AI-powered tools
            designed specifically for individuals with dyslexia.
          </p>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature) => (
            <Card key={feature.title} className="transition-transform hover:scale-[1.02]">
              <Link href={feature.href}>
                <CardHeader>
                  <div className="mb-4 p-2 w-fit rounded-lg bg-primary/10">
                    {feature.icon}
                  </div>
                  <CardTitle>{feature.title}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="ghost" className="w-full">
                    Get Started →
                  </Button>
                </CardContent>
              </Link>
            </Card>
          ))}
        </section>
      </main>

      <footer className="mt-16 text-center text-muted-foreground">
        <p>© 2024 DyslexiAssist. Making reading accessible for everyone.</p>
      </footer>
    </div>
  );
}
