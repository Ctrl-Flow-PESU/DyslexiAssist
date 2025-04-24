"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { ContrastTester } from "@/lib/ContrastTester";
import { useTheme } from "@/contexts/ThemeContext";
import Link from "next/link";

export default function ContrastTest() {
  const { setColors } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [tester] = useState(() => new ContrastTester());
  const [state, setState] = useState({
    started: false,
    completed: false,
    results: null
  });
  const [comfort, setComfort] = useState(5);
  const [currentCombo, setCurrentCombo] = useState<any>(null);
  const [currentText, setCurrentText] = useState("");

  useEffect(() => {
    setMounted(true);
  }, []);

  // Prevent hydration mismatch by not rendering until mounted
  if (!mounted) {
    return null;
  }

  const startTest = () => {
    setCurrentCombo(tester.getCurrentCombination());
    setCurrentText(tester.getCurrentText());
    setState(prev => ({ ...prev, started: true }));
  };

  const submitFeedback = () => {
    tester.recordFeedback(comfort);
    const hasNext = tester.next();

    if (hasNext) {
      setCurrentCombo(tester.getCurrentCombination());
      setCurrentText(tester.getCurrentText());
      setComfort(5);
    } else {
      setState({
        started: false,
        completed: true,
        results: tester.getResults()
      });
    }
  };

  const getBackgroundStyle = () => ({
    backgroundColor: `rgb(${currentCombo.bg.join(",")})`,
    color: `rgb(${currentCombo.text.join(",")})`,
  });

  if (state.completed && state.results) {
    return (
      <div className="min-h-screen p-8 flex items-center justify-center">
        <Card className="max-w-2xl w-full p-8">
          <h1 className="text-2xl font-bold mb-6">Test Results</h1>
          <div className="space-y-4">
            <p><strong>Best Color Combination:</strong> {state.results.best_combination}</p>
            <p><strong>Contrast Ratio:</strong> {state.results.contrast_ratio}:1</p>
            <p><strong>Comfort Rating:</strong> {state.results.comfort_rating}/10</p>
            <div className="mt-6">
              <h2 className="font-bold mb-2">Recommendations:</h2>
              <ul className="list-disc pl-6">
                {state.results.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
            <div className="flex flex-col gap-4 mt-6">
              <Button 
                onClick={() => {
                  const bestCombo = tester.dyslexicFriendlyColors.find(
                    c => c.name === state.results.best_combination
                  );
                  if (bestCombo) {
                    setColors(bestCombo.bg, bestCombo.text);
                  }
                }} 
                className="w-full"
              >
                Apply This Color Combination
              </Button>
              <Link href="/" className="w-full">
                <Button 
                  variant="outline"
                  className="w-full"
                >
                  Back to Home
                </Button>
              </Link>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8 flex items-center justify-center">
      <Card className="max-w-2xl w-full p-8">
        {!state.started ? (
          <div className="text-center space-y-6">
            <h1 className="text-2xl font-bold">Contrast Comfort Test</h1>
            <p className="text-muted-foreground">
              This test will help determine the most comfortable text and background
              color combination for your reading experience.
            </p>
            <Button onClick={startTest} size="lg">
              Start Test
            </Button>
          </div>
        ) : (
          <div className="space-y-8">
            <div 
              className="p-6 rounded-lg min-h-[200px] flex items-center justify-center text-center"
              style={getBackgroundStyle()}
            >
              <p className="text-lg">{currentText}</p>
            </div>
            
            <div>
              <p className="mb-2">Current combination: {currentCombo.name}</p>
              <p className="mb-4">How comfortable is this combination for reading?</p>
              <div className="space-y-6">
                <Slider
                  value={[comfort]}
                  onValueChange={(value) => setComfort(value[0])}
                  min={1}
                  max={10}
                  step={1}
                  className="w-full"
                />
                <div className="flex justify-between text-sm text-muted-foreground">
                  <span>Uncomfortable (1)</span>
                  <span>Very Comfortable (10)</span>
                </div>
              </div>
            </div>

            <Button 
              onClick={submitFeedback} 
              size="lg" 
              className="w-full"
            >
              Continue
            </Button>
          </div>
        )}
      </Card>
    </div>
  );
}