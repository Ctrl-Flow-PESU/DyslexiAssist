"use client";

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { NavigationMenu, NavigationMenuList, NavigationMenuItem } from "@/components/ui/navigation-menu";
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
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 font-['OpenDyslexic']">
      <div className="max-w-7xl mx-auto px-6">
        <header className="py-12"> {/* Changed mb-8 to py-12 for more vertical spacing */}
          <NavigationMenu className="w-full">
            <NavigationMenuList>
              <NavigationMenuItem>
                <h1 className="text-3xl font-bold pt-4">DyslexiAssist</h1> {/* Added pt-4 for top padding */}
              </NavigationMenuItem>
            </NavigationMenuList>
          </NavigationMenu>
        </header>

        <main className="space-y-8">
          <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature) => (
              <Card 
                key={feature.title} 
                className="transition-all duration-300 hover:border-primary/50"
              >
                <Link href={feature.href}>
                  <CardHeader className="p-6">
                    <div className="p-2.5 w-fit rounded-md bg-primary/5 mb-4">
                      {feature.icon}
                    </div>
                    <CardTitle className="text-xl mb-3">{feature.title}</CardTitle>
                    <CardDescription className="text-base leading-relaxed">
                      {feature.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="p-6 pt-0">
                    <Button 
                      variant="ghost" 
                      className="w-full text-base py-3"
                    >
                      Get Started →
                    </Button>
                  </CardContent>
                </Link>
              </Card>
            ))}
          </section>
        </main>

        <footer className="mt-12 text-center text-muted-foreground text-base">
          <p>© 2025 DyslexiAssist. Making reading accessible for everyone.</p>
        </footer>
      </div>
    </div>
  );
}
