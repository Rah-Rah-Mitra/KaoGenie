
import { QuestionSpec, Preset, PresetKey } from './types';

export const API_BASE_URL = "http://127.0.0.1:1234"; // Backend API URL

export const QUESTION_TYPES: string[] = ["MCQ", "Math Problem", "Open-Ended"];

export const PRESETS: Record<PresetKey, { name: string, specs: QuestionSpec[] }> = {
  "primary_math_quiz": {
    name: "Primary Math Quiz",
    specs: [
      { question_type: "MCQ", count: 5, prompt: "Focus on basic arithmetic and geometry definitions." },
      { question_type: "Math Problem", count: 3, prompt: "Create simple word problems involving addition and subtraction." },
    ],
  },
  "university_physics_concepts": {
    name: "University Physics Concepts",
    specs: [
      { question_type: "Open-Ended", count: 4, prompt: "Generate questions requiring detailed explanations of core physics principles like Newton's Laws or thermodynamics." },
      { question_type: "MCQ", count: 6, prompt: "Create questions that test conceptual understanding rather than complex calculations." },
    ],
  },
  "us_history_review": {
    name: "US History Review",
    specs: [
      { question_type: "MCQ", count: 10, prompt: "Focus on key dates, figures, and events in US history." },
      { question_type: "Open-Ended", count: 2, prompt: "Ask for a short analysis of the impact of a major historical event." },
    ],
  }
};

export const PRESET_OPTIONS: Preset[] = Object.entries(PRESETS).map(([key, value]) => ({
  name: value.name,
  value: key as PresetKey,
  specs: value.specs,
}));

    