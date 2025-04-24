"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { ArrowLeft, PlayCircle, StopCircle } from "lucide-react";
import Link from "next/link";

// Mock data - Replace with actual API integration
const readingTexts = {
  "Level 1": [{ 
    text: "The cat sat on the mat. It was a sunny day. The birds flew in the sky." 
  }],
  "Level 2": [{ 
    text: "Sarah loved to read books. She would visit the library on weekends. Her favorite books were about adventures." 
  }],
  "Level 3": [{ 
    text: "The quick brown fox jumps over the lazy dog. A skilled reader can understand complex sentences." 
  }]
};

export default function ReadingTest() {
  const [mounted, setMounted] = useState(false);
  const [level, setLevel] = useState("Level 1");
  const [isReading, setIsReading] = useState(false);
  const [readingSpeed, setReadingSpeed] = useState(0);
  const [startTime, setStartTime] = useState(null);
  const [speech, setSpeech] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [generatedText, setGeneratedText] = useState("");

  useEffect(() => {
    setMounted(true);
    // Initialize speech synthesis
    if (typeof window !== 'undefined') {
      const utterance = new SpeechSynthesisUtterance();
      // Add end event listener
      utterance.onend = () => {
        setIsReading(false);
        setStartTime(null);
      };
      setSpeech(utterance);
    }
  }, []);

  useEffect(() => {
    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  if (!mounted) return null;

  const generateText = async (selectedLevel: string) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/generate-text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          level: selectedLevel,
          type: 'reading' 
        }),
      });
      
      const data = await response.json();
      if (data.text) {
        setGeneratedText(data.text);
      }
    } catch (error) {
      console.error('Failed to generate text:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLevelChange = (newLevel: string) => {
    setLevel(newLevel);
    generateText(newLevel);
  };

  const handleStartReading = () => {
    setIsReading(true);
    setStartTime(Date.now());

    // Start text-to-speech
    if (speech && window.speechSynthesis) {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel();
      
      // Configure speech
      speech.text = generatedText || readingTexts[level][0].text;
      speech.rate = 1.0; // Normal speed
      speech.pitch = 1.0; // Normal pitch
      speech.volume = 1.0; // Full volume
      
      // Start speaking
      window.speechSynthesis.speak(speech);
    }
  };

  const handleStopReading = () => {
    setIsReading(false);
    // Stop speech
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    setStartTime(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 font-['OpenDyslexic']">
      <div className="max-w-6xl mx-auto p-8">
        <header className="mb-12">
          <Link href="/">
            <Button variant="ghost" className="mb-6 hover:bg-muted/50">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Home
            </Button>
          </Link>
          <div className="space-y-2">
            <h1 className="text-4xl font-bold tracking-tight">Reading Test</h1>
            <p className="text-muted-foreground text-xl leading-relaxed">
              Practice reading with texts adjusted to your level
            </p>
          </div>
        </header>

        <main className="space-y-8">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Select Reading Level</CardTitle>
                <Select value={level} onValueChange={handleLevelChange}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Select level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Level 1">Level 1 (Basic)</SelectItem>
                    <SelectItem value="Level 2">Level 2 (Intermediate)</SelectItem>
                    <SelectItem value="Level 3">Level 3 (Advanced)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <ScrollArea className="h-[200px] rounded-md border p-6">
                <div className="text-xl leading-relaxed">
                  {isLoading ? (
                    <div className="flex items-center justify-center h-full">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    </div>
                  ) : (
                    generatedText || readingTexts[level][0].text
                  )}
                </div>
              </ScrollArea>

              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <Button
                    onClick={isReading ? handleStopReading : handleStartReading}
                    className="w-full"
                    variant={isReading ? "destructive" : "default"}
                  >
                    {isReading ? (
                      <>
                        <StopCircle className="w-4 h-4 mr-2" />
                        Stop Reading
                      </>
                    ) : (
                      <>
                        <PlayCircle className="w-4 h-4 mr-2" />
                        Start Reading
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  );
}