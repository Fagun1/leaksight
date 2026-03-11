export default function Footer() {
    return (
        <footer className="bg-black border-t border-white/10 px-4 py-2 flex items-center justify-between text-[9px] font-black uppercase tracking-widest text-slate-500 shrink-0">
            <div className="flex gap-8">
                <span className="flex items-center gap-2 text-accent-lime">
                    <span className="size-1.5 rounded-full bg-accent-lime animate-pulse"></span> ENGINE: CORE_v2.4_READY
                </span>
                <span className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-[12px]">security</span> ENCRYPTED_CHANNEL_ACTIVE
                </span>
                <span className="hidden md:inline">
                    AUTH_TOKEN: <span className="text-white">A8F2-XX09-1102</span>
                </span>
            </div>
            <div className="flex gap-6 items-center">
                <span>SESSION: <span className="text-white font-mono">OPS_ANALYST_049</span></span>
                <span>LATENCY: <span className="text-accent-lime glow-text">24MS</span></span>
                <div className="flex gap-1">
                    <div className="size-1 bg-accent-lime"></div>
                    <div className="size-1 bg-accent-lime/60"></div>
                    <div className="size-1 bg-accent-lime/30"></div>
                </div>
            </div>
        </footer>
    );
}
