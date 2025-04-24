"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { FolderOpen, ArrowLeft, FileText } from "lucide-react";
import Link from "next/link";

export default function OpenFile() {
  const [text, setText] = useState("");
  const [fileName, setFileName] = useState("");
  const fileInputRef = useRef(null);
  const textAreaRef = useRef(null);

  useEffect(() => {
    if (text && textAreaRef.current) {
      textAreaRef.current.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      });
    }
  }, [text]);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      setFileName(file.name);
      const text = await file.text();
      setText(text);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleDrop = async (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      setFileName(file.name);
      const text = await file.text();
      setText(text);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 font-['OpenDyslexic']">
      <div className="max-w-6xl mx-auto p-8">
        <header className="mb-12">
          <Link href="/">
            <Button variant="ghost" className="mb-6 hover:bg-muted/50 font-['OpenDyslexic']">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Home
            </Button>
          </Link>
          <div className="space-y-2">
            <h1 className="text-4xl font-bold tracking-tight">Open Text File</h1>
            <p className="text-muted-foreground text-xl leading-relaxed">
              Import and analyze text files with dyslexia-friendly formatting
            </p>
          </div>
        </header>

        <main className="space-y-8">
          <Card 
            className="border-2 border-dashed border-primary/30 hover:border-primary/70 
                       transition-all duration-300 bg-card/50 backdrop-blur-sm"
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <CardContent className="flex flex-col items-center justify-center p-16 text-center">
              <div className="p-4 rounded-full bg-primary/10 mb-6">
                <FolderOpen className="w-12 h-12 text-primary" />
              </div>
              <h2 className="text-2xl font-semibold mb-3">
                {fileName || "Upload your text file"}
              </h2>
              <p className="text-muted-foreground mb-6 max-w-md">
                Drag and drop your text file here, or click the button below to select from your computer
              </p>
              <input
                type="file"
                accept=".txt,.doc,.docx,.rtf,.pdf"
                className="hidden"
                onChange={handleFileUpload}
                ref={fileInputRef}
              />
              <Button 
                onClick={() => fileInputRef.current?.click()}
                className="min-w-[200px] text-lg py-6"
                size="lg"
              >
                Choose File
              </Button>
            </CardContent>
          </Card>

          {text && (
            <div className="space-y-6 animate-in fade-in-50" ref={textAreaRef}>
              <Card className="border-primary/20">
                <CardHeader className="flex flex-row items-center justify-between">
                  <div className="flex items-center gap-3">
                    <FileText className="w-5 h-5 text-primary" />
                    <h3 className="text-2xl font-semibold">{fileName}</h3>
                  </div>
                  <Badge variant="secondary">
                    {fileName.split('.').pop().toUpperCase()}
                  </Badge>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[500px] w-full rounded-md border p-4">
                    <div className="text-xl leading-relaxed whitespace-pre-wrap font-['OpenDyslexic']">
                      {text}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}