import type { VariantProps } from "class-variance-authority"
import { cva } from "class-variance-authority"

export { default as Badge } from "./Badge.vue"

export const badgeVariants = cva(
  "inline-flex items-center justify-center rounded-lg border px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-[color,box-shadow] overflow-hidden",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground [a&]:hover:bg-primary/90",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground [a&]:hover:bg-secondary/90",
        destructive:
         "border-transparent bg-destructive text-white [a&]:hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60",
        outline:
          "text-foreground [a&]:hover:bg-accent [a&]:hover:text-accent-foreground",
        rdf:
          "border-transparent bg-blue-200 text-gray-800 dark:bg-secondary dark:text-blue-200 ",
        ontology:
          "border-transparent bg-red-200 text-gray-800 dark:bg-secondary dark:text-red-200",
        select:
          "border-transparent bg-green-200 text-slate-800 dark:bg-secondary dark:text-green-200 ",
        ask:
          "border-transparent bg-indigo-200 text-gray-800 dark:bg-secondary dark:text-indigo-200",
        construct:
          "border-transparent bg-orange-200 text-gray-800 dark:bg-secondary dark:text-orange-200",
        describe:
          "border-transparent bg-yellow-200 text-gray-600 dark:bg-secondary dark:text-yellow-200",
        active:
          "border-transparent bg-green-200 text-slate-800 dark:bg-secondary dark:text-green-200",
        inactive:
          "border-transparent bg-red-200 text-gray-800 dark:bg-secondary dark:text-red-200",

      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
)
export type BadgeVariants = VariantProps<typeof badgeVariants>
