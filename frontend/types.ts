
export interface QuestionSpec {
  question_type: string;
  count: number;
  prompt?: string | null;
}

export interface ExamFromTopicRequest {
  subject: string;
  grade_level: string;
  exam_title: string;
  question_specs: QuestionSpec[];
}

export interface GeneratedSolution {
  explanation: string;
  final_answer?: string | null;
  correct_option_index?: number | null;
}

export interface ExamQuestion {
  id: string;
  question_type: string;
  question_text: string;
  options?: string[] | null;
  image_url?: string | null;
  solution: GeneratedSolution;
}

export interface IngestionSummary {
  message: string;
  processed_sources_count: number;
  total_chunks_ingested: number;
  collections_created: string[];
  ingested_sources: string[];
}

export interface FullExam {
  exam_id: string;
  ingestion_summary: IngestionSummary;
  exam_title: string;
  exam_paper_markdown: string;
  answer_key_markdown: string;
  questions: ExamQuestion[];
  sources_used: string[];
}

// Helper type for QuestionSpec with a local ID for list rendering
export interface QuestionSpecRow extends QuestionSpec {
  localId: string;
}

export type PresetKey = "primary_math_quiz" | "university_physics_concepts" | "us_history_review";

export interface Preset {
  name: string;
  value: PresetKey;
  specs: QuestionSpec[];
}