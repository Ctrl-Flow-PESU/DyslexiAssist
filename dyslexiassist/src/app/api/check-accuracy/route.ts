import { Groq } from "groq-sdk";
import { NextResponse } from "next/server";

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY!,
});

export async function POST(request: Request) {
  try {
    const { userInput, expectedText } = await request.json();

    // Input validation
    if (!userInput || !expectedText) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    const completion = await groq.chat.completions.create({
      messages: [
        {
          role: "system",
          content: "You are an AI that analyzes text accuracy for dyslexic students. You must respond with valid JSON only."
        },
        {
          role: "user",
          content: `Analyze these texts and respond with ONLY a JSON object (no markdown, no code blocks):
Expected: "${expectedText}"
Submitted: "${userInput}"

Required JSON structure:
{
  "correct": boolean,
  "message": "string with encouraging feedback",
  "similarity": number between 0-100,
  "errors": ["array of specific error descriptions"]
}`
        }
      ],
      model: "llama-3.3-70b-versatile",
      temperature: 0.3,
      max_tokens: 500,
    });

    const responseText = completion.choices[0]?.message?.content?.trim();
    if (!responseText) {
      throw new Error('No response from AI');
    }

    // Clean the response text to ensure valid JSON
    const cleanedResponse = responseText
      .replace(/```json/g, '')
      .replace(/```/g, '')
      .trim();

    try {
      const analysis = JSON.parse(cleanedResponse);
      
      // Ensure all required fields exist with correct types
      const validAnalysis = {
        correct: Boolean(analysis.correct),
        message: String(analysis.message || "Analysis completed"),
        similarity: Number(analysis.similarity || 0),
        errors: Array.isArray(analysis.errors) ? analysis.errors : []
      };

      return NextResponse.json(validAnalysis);
    } catch (parseError) {
      console.error('JSON parse error:', parseError, 'Response:', responseText);
      // Return a fallback response instead of throwing
      return NextResponse.json({
        correct: false,
        message: "Unable to analyze text properly. Please try again.",
        similarity: 0,
        errors: [`Error analyzing text: ${parseError.message}`]
      }, { status: 200 });
    }
  } catch (error) {
    console.error('Error analyzing text:', error);
    return NextResponse.json({
      correct: false,
      message: "Failed to process text comparison",
      similarity: 0,
      errors: [error instanceof Error ? error.message : "Unknown error"]
    }, { status: 200 });
  }
}