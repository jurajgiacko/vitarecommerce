export type Profile = {
  id: string;
  name: string;
  email: string;
  initials: string;
  role: string;
  color: string;
  lastActiveAt?: string | null;
};

export type ChannelDecision = {
  channel: string;
  decision: string;
  role: string;
  priority: number;
};

export type Review = {
  id: string;
  profileId: string;
  profileName: string;
  profileInitials: string;
  profileColor: string;
  status: string;
  categoryKey: string;
  categoryLabel: string;
  portfolioRole: string;
  lifecycleDecision: string;
  confidence: string;
  rationale: string;
  channels: ChannelDecision[];
  updatedAt: string;
};

export type SourceSummary = {
  id: string;
  sourceKey: string;
  sourceSite: string;
  url: string;
  name: string;
  sku: string;
  ean: string;
  priceCzk: string | null;
  imageUrl: string;
  description: string;
  quality: Record<string, boolean>;
};

export type Comment = {
  id: string;
  profileId: string;
  profileName: string;
  profileInitials: string;
  profileColor: string;
  body: string;
  createdAt: string;
};

export type FinalDecision = {
  id: string;
  categoryKey: string;
  categoryLabel: string;
  portfolioRole: string;
  lifecycleDecision: string;
  status: string;
  rationale: string;
  approvedByProfileId: string;
  channels: ChannelDecision[];
  updatedAt: string;
};

export type WorkbenchProduct = {
  id: string;
  name: string;
  brand: string;
  sku: string;
  ean: string;
  categoryKey: string;
  categoryLabel: string;
  categoryConfidence: string;
  formKey: string;
  formLabel: string;
  description: string;
  imageUrl: string;
  priceCzk: string | null;
  sourceCount: number;
  lifecycle: string;
  manuallyCreated: boolean;
  familyKey: string;
  familyName: string;
  familySize: number;
  coverage: Record<string, boolean>;
  quality: {
    hasSku: boolean;
    hasEan: boolean;
    hasImage: boolean;
    hasDescription: boolean;
    hasLongContent: boolean;
    hasPrice: boolean;
    hasConflict: boolean;
    hasVariation?: boolean;
  };
  fieldConflicts: Array<{ field?: string; values?: string[]; severity?: string }>;
  systemRecommendation: {
    channels: string[];
    primary?: string;
    confidence: string;
    reason: string;
  };
  sources: SourceSummary[];
  reviews: Review[];
  comments: Comment[];
  finalDecision: FinalDecision | null;
  consensusConflict: boolean;
};

export type SaveFeedbackState = "idle" | "saving" | "saved" | "error";

export type SaveFeedbackHandler = (state: SaveFeedbackState, message: string) => void;

export type WorkbenchData = {
  profile: Profile;
  profiles: Profile[];
  round: {
    id: string;
    name: string;
    description: string;
    status: string;
    dueAt: string | null;
  };
  products: WorkbenchProduct[];
  crawl: {
    sitemapUrlCount: number;
    sourceProductCount: number;
    masterProductCount: number;
    errorCount: number;
    completedAt: string;
    summary: Record<string, unknown>;
  } | null;
};

export type ProductDetail = {
  productId: string;
  sources: Array<SourceSummary & { contentSections: Record<string, string> }>;
  audit: Array<{
    id: string;
    action: string;
    actorName: string;
    createdAt: string;
    payload: Record<string, unknown>;
  }>;
};
