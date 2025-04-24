"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ArrowLeft, PlayCircle, CheckCircle } from "lucide-react";
import Link from "next/link";

export default function DictationTest() {
  const [mounted, setMounted] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [userInput, setUserInput] = useState("");
  const [currentText, setCurrentText] = useState("");
  const [level, setLevel] = useState("basic");
  const [feedback, setFeedback] = useState<{ correct: boolean; message: string } | null>(null);
  const [speech, setSpeech] = useState<SpeechSynthesisUtterance | null>(null);

  useEffect(() => {
    setMounted(true);
    if (typeof window !== 'undefined') {
      const utterance = new SpeechSynthesisUtterance();
      utterance.onend = () => setIsPlaying(false);
      setSpeech(utterance);
      generateText(level);
    }
  }, []);

  const generateText = async (difficulty: string) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/generate-text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          level: difficulty,
          type: 'dictation' 
        }),
      });
      
      const data = await response.json();
      if (data.text) {
        setCurrentText(data.text);
      }
    } catch (error) {
      console.error('Failed to generate text:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePlay = () => {
    if (speech && window.speechSynthesis) {
      setIsPlaying(true);
      window.speechSynthesis.cancel();
      
      speech.text = currentText;
      speech.rate = 0.8; // Slightly slower for better comprehension
      speech.pitch = 1.0;
      speech.volume = 1.0;
      
      window.speechSynthesis.speak(speech);
    }
  };

  const checkAccuracy = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/check-accuracy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userInput: userInput.trim(),
          expectedText: currentText.trim()
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to analyze text');
      }

      if (data.error) {
        throw new Error(data.error);
      }

      setFeedback({
        correct: data.correct,
        message: `${data.message} ${
          data.similarity 
            ? `(${Math.round(data.similarity)}% similar)` 
            : ''
        }`
      });

      if (data.errors?.length > 0) {
        setFeedback(prev => ({
          correct: prev?.correct || false,
          message: `${prev?.message}\n\nSpecific areas to work on:\n${data.errors.join('\n')}`
        }));
      }

    } catch (error) {
      console.error('Error checking accuracy:', error);
      setFeedback({
        correct: false,
        message: error instanceof Error ? error.message : "Sorry, there was an error checking your answer. Please try again."
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLevelChange = (newLevel: string) => {
    setLevel(newLevel);
    setUserInput("");
    setFeedback(null);
    generateText(newLevel);
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
            <h1 className="text-4xl font-bold tracking-tight">Dictation Test</h1>
            <p className="text-muted-foreground text-xl leading-relaxed">
              Listen carefully and type what you hear
            </p>
          </div>
        </header>

        <main className="space-y-8">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Write What You Hear</CardTitle>
                <Select value={level} onValueChange={handleLevelChange}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Select level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="basic">Basic (1-2 sentences)</SelectItem>
                    <SelectItem value="intermediate">Intermediate (3-4 sentences)</SelectItem>
                    <SelectItem value="advanced">Advanced (Complex paragraph)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex gap-4">
                <Button 
                  onClick={handlePlay}
                  className="flex-1"
                  disabled={isPlaying || isLoading}
                >
                  <PlayCircle className="w-4 h-4 mr-2" />
                  {isPlaying ? "Playing..." : "Play Text"}
                </Button>
                <Button 
                  onClick={() => generateText(level)}
                  variant="outline"
                  disabled={isLoading}
                >
                  New Text
                </Button>
              </div>

              {isLoading ? (
                <div className="flex items-center justify-center h-[120px]">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : (
                <Textarea
                  placeholder="Type the text you hear..."
                  className="min-h-[120px] text-lg"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                />
              )}

              <Button 
                onClick={checkAccuracy}
                className="w-full"
                disabled={!userInput}
              >
                <CheckCircle className="w-4 h-4 mr-2" />
                Check Answer
              </Button>

              {feedback && (
                <div className={`p-4 rounded-lg ${
                  feedback.correct 
                    ? "bg-green-500/10 text-green-500" 
                    : "bg-red-500/10 text-red-500"
                }`}>
                  <p className="text-lg">{feedback.message}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  );
}