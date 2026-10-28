import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const lessons = defineCollection({
  loader: glob({ pattern: "**/*.mdx", base: "./src/content/lessons" }),
  schema: z.object({
    title: z.string(),
    module: z.number(),
    moduleTitle: z.string(),
    lessonNumber: z.number().nullable(),
    order: z.number(),
    notebookFile: z.string(),
    colabRepo: z.string().default("YOUR_GH_USERNAME/comprehensive-numpy"),
    exerciseIds: z.array(z.string()).default([]),
    kind: z.enum(["overview", "lesson"]).default("lesson"),
  }),
});

export const collections = { lessons };
