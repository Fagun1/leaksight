"use client";

import { usePosts } from "@/hooks/usePosts";

export default function RecentPosts() {
  const { data, isLoading, error } = usePosts({ per_page: 10 });

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="h-16 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <p className="text-slate-500">Could not load posts. Check API connection.</p>
    );
  }

  const posts = data?.data ?? [];

  if (posts.length === 0) {
    return (
      <p className="text-slate-500">
        No posts yet. Run <code className="bg-slate-200 dark:bg-slate-700 px-1 rounded">python -m infra.scripts.seed_db</code> to add sample data.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {posts.map((post: any) => (
        <div
          key={post.id ?? post._id}
          className="p-4 bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800"
        >
          <div className="flex justify-between items-start">
            <div className="flex-1 min-w-0">
              <p className="text-sm text-slate-900 dark:text-white line-clamp-2">
                {post.cleaned_content || post.content || post.title}
              </p>
              <div className="flex gap-2 mt-2 text-xs text-slate-500">
                <span>{post.source_platform}</span>
                <span>•</span>
                <span>{post.author_username}</span>
                {post.is_leak && (
                  <>
                    <span>•</span>
                    <span className="text-cyan-600">Leak</span>
                  </>
                )}
              </div>
            </div>
            {post.source_url && (
              <a
                href={post.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-2 text-cyan-600 hover:underline text-xs shrink-0"
              >
                View
              </a>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
