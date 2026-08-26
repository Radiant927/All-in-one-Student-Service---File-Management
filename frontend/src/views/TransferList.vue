<template>
  <div class="page">
    <div class="page-header">
      <h2 class="page-title">转交记录</h2>
      <div class="header-actions">
        <el-button :icon="Download" :loading="exporting" @click="onExport">导出 Excel</el-button>
        <el-button type="primary" :icon="CirclePlus" @click="router.push({ name: 'transfer-new' })">
          发起转交
        </el-button>
      </div>
    </div>

    <el-card class="card-gap">
      <el-form :model="filters" inline @submit.prevent>
        <el-form-item label="范围">
          <el-select v-model="filters.role" placeholder="全部" clearable style="width: 130px">
            <el-option label="我发起的" value="sent" />
            <el-option label="发给我的" value="received" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width: 120px">
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filters.file_type" placeholder="全部" clearable style="width: 130px">
            <el-option
              v-for="item in fileTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="紧急度">
          <el-select v-model="filters.urgency" placeholder="全部" clearable style="width: 110px">
            <el-option
              v-for="item in urgencyOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="创建日期">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            start-placeholder="开始"
            end-placeholder="结束"
            style="width: 230px"
          />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="filters.keyword"
            placeholder="编号 / 标题 / 姓名"
            clearable
            style="width: 190px"
            @keyup.enter="search"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="search">查询</el-button>
          <el-button :icon="Refresh" @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-loading="loading">
      <el-table :data="items" @row-click="goDetail">
        <el-table-column prop="transfer_no" label="编号" width="170" />
        <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" effect="light">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="紧急度" width="90">
          <template #default="{ row }">
            <el-tag :type="urgencyType(row.urgency)" effect="plain" size="small">
              {{ urgencyLabel(row.urgency) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="100">
          <template #default="{ row }">{{ fileTypeLabel(row.file_type) }}</template>
        </el-table-column>
        <el-table-column label="方向" width="180">
          <template #default="{ row }">
            {{ campusLabel(row.from_campus) }} → {{ campusLabel(row.to_campus) }}
          </template>
        </el-table-column>
        <el-table-column prop="courier_name" label="转交同学" width="100" />
        <el-table-column label="发车时间" width="140">
          <template #default="{ row }">{{ formatDateTime(row.depart_time) }}</template>
        </el-table-column>
        <el-table-column label="附件" width="70">
          <template #default="{ row }">{{ row.files?.length || 0 }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click.stop="goDetail(row)">详情</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="没有符合条件的转交单" />
        </template>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        class="pagination"
        @current-change="loadList"
        @size-change="search"
      />
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { CirclePlus, Download, Refresh, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

import * as transfersApi from '@/api/transfers'
import * as statsApi from '@/api/stats'
import {
  FILE_TYPE,
  TRANSFER_STATUS,
  URGENCY,
  campusLabel,
  fileTypeLabel,
  formatDateTime,
  statusLabel,
  statusType,
  toOptions,
  urgencyLabel,
  urgencyType,
} from '@/utils/dict'

const route = useRoute()
const router = useRouter()

const statusOptions = toOptions(TRANSFER_STATUS)
const fileTypeOptions = toOptions(FILE_TYPE)
const urgencyOptions = toOptions(URGENCY)

const loading = ref(false)
const exporting = ref(false)
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const dateRange = ref(null)

const filters = ref({
  role: route.query.role || '',
  status: route.query.status || '',
  file_type: '',
  urgency: '',
  keyword: '',
})

/** 空值必须剔除，否则后端枚举校验会因为空字符串报 422 */
const queryParams = computed(() => {
  const params = {}
  for (const [key, value] of Object.entries(filters.value)) {
    if (value) params[key] = value
  }
  if (dateRange.value?.length === 2) {
    params.date_from = dateRange.value[0]
    params.date_to = dateRange.value[1]
  }
  return params
})

async function loadList() {
  loading.value = true
  try {
    const data = await transfersApi.listTransfers({
      ...queryParams.value,
      page: page.value,
      page_size: pageSize.value,
    })
    items.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function search() {
  page.value = 1
  loadList()
}

function resetFilters() {
  filters.value = { role: '', status: '', file_type: '', urgency: '', keyword: '' }
  dateRange.value = null
  search()
}

function goDetail(row) {
  router.push({ name: 'transfer-detail', params: { id: row.id } })
}

async function onExport() {
  exporting.value = true
  try {
    await statsApi.exportTransfers(queryParams.value)
    ElMessage.success('导出完成')
  } finally {
    exporting.value = false
  }
}

onMounted(loadList)
</script>

<style scoped>
.header-actions {
  display: flex;
  gap: 8px;
}

.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}

:deep(.el-table__row) {
  cursor: pointer;
}
</style>
