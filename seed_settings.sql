insert into settings (key, value, updated_at, updated_by)
values
  ('system_prompt', 'Вы практичный ИИ-консультант по домашней птице. Отвечайте кратко, спокойно, по делу, всегда на русском языке и на "вы".', now(), 'system'),
  ('system_prompt_version', '1', now(), 'system'),
  ('primary_chat_model', 'google/gemini-2.5-pro', now(), 'system'),
  ('fallback_chat_model', 'anthropic/claude-sonnet-4-5', now(), 'system'),
  ('summary_model', 'google/gemini-2.0-flash', now(), 'system')
on conflict (key) do nothing;