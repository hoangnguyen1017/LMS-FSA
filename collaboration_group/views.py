from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required  # To ensure user is logged in
from .forms import CollaborationGroupForm
from .models import CollaborationGroup
from collaboration_member.models import GroupMember
from user.models import User

# Display all collaboration groups
@login_required
def collaboration_group_list(request):
    collaboration_groups = CollaborationGroup.objects.select_related('created_by', 'course').all()
    return render(request, 'collaboration_group_list.html', {'collaboration_groups': collaboration_groups})

# Create a new collaboration group (only logged-in user can create)
@login_required
def collaboration_group_add(request):
    if request.method == 'POST':
        form = CollaborationGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user  # Set the creator to the logged-in user
            group.save()
            return redirect('collaboration_group:collaboration_group_list')
    else:
        form = CollaborationGroupForm()
    
    return render(request, 'collaboration_group_form.html', {'form': form})

# Edit a collaboration group (group creator or admin can edit)
@login_required
def collaboration_group_edit(request, pk):
    collaboration_group = get_object_or_404(CollaborationGroup, pk=pk)
    
    # Ensure only the creator or admin can edit the group
    if request.user != collaboration_group.created_by and not request.user.is_staff:
        return redirect('collaboration_group:collaboration_group_list')

    if request.method == 'POST':
        form = CollaborationGroupForm(request.POST, instance=collaboration_group)
        if form.is_valid():
            form.save()
            return redirect('collaboration_group:collaboration_group_list')
    else:
        form = CollaborationGroupForm(instance=collaboration_group)

    return render(request, 'collaboration_group_form.html', {'form': form})

# Delete a collaboration group (group creator or admin can delete)
@login_required
def collaboration_group_delete(request, pk):
    collaboration_group = get_object_or_404(CollaborationGroup, pk=pk)
    
    # Ensure only the creator or admin can delete the group
    if request.user != collaboration_group.created_by and not request.user.is_staff:
        return redirect('collaboration_group:collaboration_group_list')

    if request.method == 'POST':
        collaboration_group.delete()
        return redirect('collaboration_group:collaboration_group_list')

    return render(request, 'collaboration_group_confirm_delete.html', {'collaboration_group': collaboration_group})

# Manage group members (group creator or admin can manage members)
@login_required
def manage_group(request, group_id):
    group = get_object_or_404(CollaborationGroup, pk=group_id)

    # Ensure only the group creator or admin can manage the group
    if request.user != group.created_by and not request.user.is_staff:
        return redirect('collaboration_group:collaboration_group_list')

    members = GroupMember.objects.filter(group=group)
    all_users = User.objects.exclude(id__in=members.values_list('user_id', flat=True))  # Exclude existing members

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            user = get_object_or_404(User, pk=user_id)
            if not GroupMember.objects.filter(group=group, user=user).exists():  # Prevent duplicate members
                GroupMember.objects.create(group=group, user=user)
            return redirect('collaboration_group:manage_group', group_id=group.id)

    return render(request, 'manage_group.html', {
        'group': group,
        'members': members,
        'all_users': all_users,
    })

# Remove a group member (group creator or admin can remove members)
@login_required
def remove_member(request, group_id, member_id):
    group = get_object_or_404(CollaborationGroup, pk=group_id)

    # Ensure only the group creator or admin can remove members
    if request.user != group.created_by and not request.user.is_staff:
        return redirect('collaboration_group:manage_group', group_id=group_id)

    member = get_object_or_404(GroupMember, pk=member_id, group_id=group_id)
    member.delete()
    return redirect('collaboration_group:manage_group', group_id=group_id)
