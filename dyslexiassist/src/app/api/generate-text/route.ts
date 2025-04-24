import { Groq } from "groq-sdk";
import { NextResponse } from "next/server";

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY!,
});

export async function POST(request: Request) {
  try {
    const { level, type } = await request.json();

    let prompt = "";
    if (type === "dictation") {
      switch (level) {
        case "basic":
          prompt = "Generate 1-2 simple sentences suitable for a dictation test for dyslexic students. Use basic vocabulary and clear sentence structure.";
          break;
        case "intermediate":
          prompt = "Generate 3-4 sentences suitable for a dictation test for dyslexic students. Include some compound sentences and moderately complex vocabulary.";
          break;
        case "advanced":
          prompt = "Generate a complex paragraph suitable for a dictation test for dyslexic students. Use varied sentence structures while maintaining clarity.";
          break;
        default:
          prompt = "Generate 1-2 simple sentences for a dictation test.";
      }
    } else {
      // Original reading test prompts
      switch (level) {
        case "Level 1":
          prompt = "Generate a simple paragraph suitable for elementary reading level. Use basic vocabulary and short sentences.";
          break;
        case "Level 2":
          prompt = "Generate a moderate length text suitable for intermediate reading level. Use varied vocabulary and sentence structures.";
          break;
        case "Level 3":
          prompt = "Generate an advanced text passage with complex sentence structures and sophisticated vocabulary.";
          break;
        default:
          prompt = "Generate a simple reading passage.";
      }
    }

    const completion = await groq.chat.completions.create({
      messages: [
        {
          role: "system",
          content: "You are a helpful assistant that generates appropriate text for reading and dictation practice, specialized for dyslexic users."
        },
        {
          role: "user",
          content: prompt
        }
      ],
      model: "llama-3.3-70b-versatile",
      temperature: 0.7,
      max_tokens: 150,
    });

    const generatedText = completion.choices[0]?.message?.content || "";

    return NextResponse.json({ text: generatedText });
  } catch (error) {
    console.error('Error generating text:', error);
    return NextResponse.json(
      { error: 'Failed to generate text' },
      { status: 500 }
    );
  }
}