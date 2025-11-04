"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface CashFlowChartProps {
  data: Array<{
    date: string;
    income: number;
    expense: number;
    balance: number;
  }>;
}

export function CashFlowChart({ data }: CashFlowChartProps) {
  const formattedData = data.map(item => ({
    date: new Date(item.date).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
    Receitas: item.income,
    Despesas: item.expense,
    Saldo: item.balance,
  }));

  return (
    <Card className="col-span-4">
      <CardHeader>
        <CardTitle>Fluxo de Caixa</CardTitle>
        <CardDescription>Últimos 7 dias</CardDescription>
      </CardHeader>
      <CardContent className="pl-2">
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={formattedData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip 
              formatter={(value: number) => 
                new Intl.NumberFormat('pt-BR', { 
                  style: 'currency', 
                  currency: 'BRL' 
                }).format(value)
              }
            />
            <Legend />
            <Line type="monotone" dataKey="Receitas" stroke="#10b981" strokeWidth={2} />
            <Line type="monotone" dataKey="Despesas" stroke="#ef4444" strokeWidth={2} />
            <Line type="monotone" dataKey="Saldo" stroke="#3b82f6" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
