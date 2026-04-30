
import { cn } from '../lib/utils';

export const KPICard = ({ title, value, change, isPositive, icon: Icon, unit = "", hideChange = false }: any) => (
  <div className="card-3d rounded-2xl p-6 flex flex-col gap-4">
    <div className="flex justify-between items-start">
      <div className="w-10 h-10 rounded-lg bg-natural-sage/10 flex items-center justify-center text-natural-sage">
        <Icon className="w-5 h-5" />
      </div>
      {!hideChange && change !== undefined && (
        <div className={cn("px-2 py-1 rounded-md text-xs font-semibold flex items-center gap-1", isPositive ? "bg-emerald-50 text-emerald-600" : "bg-red-50 text-red-600")}>
          {isPositive ? '+' : '-'}{Math.abs(change)}%
        </div>
      )}
    </div>
    <div>
      <h3 className="text-natural-charcoal/50 text-sm font-medium mb-1">{title}</h3>
      <p className="text-2xl font-semibold text-natural-charcoal">
        {unit === "$" ? "$" : ""}{value}{unit !== "$" ? unit : ""}
      </p>
    </div>
  </div>
);
